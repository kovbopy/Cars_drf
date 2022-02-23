from django.db import models
from django.db.models import Avg
from users.models import User


class CarManager(models.Manager):
    def get_queryset(self):
        return super(CarManager, self).get_queryset().\
                              select_related('owner').\
                              prefetch_related('users')

class Car(models.Model):
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='owned_cars')
    users = models.ManyToManyField(User, through='UserCar')
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_speed=models.IntegerField(default=0)
    entries=models.PositiveSmallIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2,default=None, null=True)
    objects=CarManager()

    def __str__(self):
        return self.name


class UserCarManager(models.Manager):
    def get_queryset(self):
        return super(UserCarManager, self).get_queryset().\
                                select_related('user','car')

class UserCar(models.Model):
    RATE= (
        (1, 1),(2, 2),(3,3),
        (4, 4),(5, 5)
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    rate=models.IntegerField(choices=RATE,null=True)
    objects=UserCarManager()

    class Meta:
        unique_together=["user","car"]


    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)

        car = self.car
        car.rating = UserCar.objects.filter(car=car). \
                                     aggregate(rating=Avg('rate')). \
                                     get('rating')
        car.save()





