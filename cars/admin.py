from django.contrib import admin
from .models import Car, UserCar
from .signals import ObjectAction


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'id', 'owner', 'max_speed')

admin.site.register(ObjectAction)
admin.site.register(UserCar)
