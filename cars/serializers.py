from rest_framework import serializers
from cars.models import Car, UserCar

max_speed_overall = 0

class CarSerializer(serializers.ModelSerializer):
    max_speed_overall = serializers.SerializerMethodField('_max_speed_overall')
    owned_by = serializers.CharField(source='owner.email',read_only=True)
    likes = serializers.IntegerField(read_only=True)
    dislikes = serializers.IntegerField(read_only=True)
    sum=serializers.IntegerField(read_only=True)


    def _max_speed_overall(self, car):
        global max_speed_overall
        max_speed = int(getattr(car, 'max_speed'))
        if max_speed and max_speed > max_speed_overall:
            max_speed_overall = max_speed
            return max_speed_overall
        else:
            return max_speed_overall

    class Meta:
        model = Car
        fields = ('id', 'name', 'description', 'max_speed', 'max_speed_overall',
                  "owned_by","entries","likes","dislikes","sum","rating")
        depth = 1


class UserCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCar
        fields = ("id","user",'car','like',"rate")