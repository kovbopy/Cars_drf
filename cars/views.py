from django.db import IntegrityError
from django.db.models import Q, F, Count, Case, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cars.models import Car, UserCar
from cars.permissions import CarPermission
from cars.serializers import CarSerializer, UserCarSerializer
from users.models import User
from .utils import get_client_ip, logger
from .utils import ThreadEmail


class CarViewSet(viewsets.ModelViewSet):
    serializer_class = CarSerializer
    permission_classes = [CarPermission]
    throttle_scope = 'car_throttle'
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,SearchFilter,
                       OrderingFilter]
    filter_fields=["max_speed"]
    search_fields = ["name","^description","=owner__email"]
    ordering_field=["max_speed","name"]
    # ?max_speed=1 ?search=tesla ?ordering=max_speed

    def get_queryset(self):
        cars=Car.objects.annotate(
                         likes=Count(Case(When(usercar__like=True, then=1))),
                         dislikes=Count(Case(When(usercar__like=False, then=1))),
                         sum=F("likes") - F('dislikes')
        )
        return cars


# users can also search cars in a chosen max_speed range
    def retrieve(self, request, *args, **kwargs):
        current_owner=User.objects.get(id=request.user.id)
        if current_owner.ip=="ip":
           current_owner.ip=get_client_ip(request)
           current_owner.save()

        pkk=kwargs['pk']
        if "max_speed" in pkk:
          pkk_list = [i for i in pkk]
          m_index = pkk_list.index("m")
          d_index = pkk_list.index("d")
          logger.info("filtered by max_speed",extra={"user":request.user,
                                                     "request_method":request.method})

          global cars
          if ">" in pkk_list[:m_index] and ">" in pkk_list[d_index:]:
            cars = Car.objects.filter(Q(max_speed__lt=pkk[:m_index-1]) &
                                      Q(max_speed__gt=pkk[d_index+2:]))
          elif ">" in pkk_list[d_index:]:
            cars = Car.objects.filter(Q(max_speed__gt=pkk[d_index+2:]))
          elif "<" in pkk_list[d_index:]:
            cars = Car.objects.filter(Q(max_speed__lt=pkk[d_index + 2:]))

        else:
           logger.info("",extra={"user":request.user,"request_method":request.method,
                                 "model_id":"car_"+pkk})

           cars = Car.objects.filter(pk=pkk)
           cars.update(entries=F('entries') + 1)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        current_owner = User.objects.get(id=request.user.id)
        if current_owner.ip == "ip":
            current_owner.ip = get_client_ip(request)
            current_owner.save()

        data = request.data
        new_car = Car.objects.create(name=data["name"].lower(),
                                     description=data["description"].lower(),
                                     max_speed=data['max_speed'],
                                     owner=request.user)
        new_car.save()
        serializer = CarSerializer(new_car)
        return Response(serializer.data)


    def update(self, request, *args, **kwargs):
        car = self.get_object()
        data = request.data

        car.name = data["name"].lower()
        car.description = data["description"].lower()
        car.max_speed=data['max_speed']
        car.save()
        serializer = CarSerializer(car)

        logger.info("",extra={"user":request.user,"request_method": request.method,
                              "model_id":"car_"+str(car.id)})
        return Response(serializer.data)


    def partial_update(self, request, *args, **kwargs):
        car = self.get_object()
        data = request.data

        car.name = data.get('name',car.name).lower()
        car.description = data.get('description',car.description).lower()
        car.max_speed = data.get('max_speed',car.max_speed)
        car.save()
        serializer = CarSerializer(car)

        logger.info("",extra={"user":request.user,"request_method": request.method,
                              "model_id":"car_"+str(car.id)})
        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        car = self.get_object()
        try:
            ThreadEmail(f"Your car (id:{car.id},name:{car.name}) has been deleted "
                             f"by {request.user}", "Car deleted", [car.owner.email, ])\
                             .start()
        except:
            pass
        car_id=str(car.id)
        car.delete()
        return Response('Car with id '+car_id+" has been deleted")


class CarUserViewSet(viewsets.ModelViewSet):
    queryset = UserCar.objects.all()
    serializer_class = UserCarSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
           user_car = UserCar.objects.create(user=request.user,
                                             like=data["like"],
                                             rate=data["rate"],
                                             car=Car.objects.get(name=data['car']))
           user_car.save()
           serializer = UserCarSerializer(user_car)
           return Response(serializer.data)
        except IntegrityError:
            return Response('You already liked/disliked this car')
        except:
            return Response('Error')


    def partial_update(self, request, *args, **kwargs):
        user_car = self.get_object()
        data = request.data
        if request.user!=user_car.user:
            return Response('You are not authorized to perform this action')

        user_car.like = data.get('like',user_car.like)
        user_car.rate = data.get('rate', user_car.rate)
        user_car.save()
        serializer = UserCarSerializer(user_car)
        return Response(serializer.data)



