from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from cars.models import Car
from users.models import User
from django.dispatch import receiver


class ObjectAction(models.Model):
    ACTIONS=(("created","created"),
             ("deleted","deleted"))
    user= models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)
    action_type=models.CharField(choices=ACTIONS,max_length=10)
    content_type= models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id= models.PositiveIntegerField()
    content_object= GenericForeignKey('content_type', 'object_id')
    timestamp= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action_type} {str(self.content_type)[-3:]} " \
               f"with id {self.object_id} in {str(self.timestamp)[:-6]}"


@receiver(post_save,sender=Car)
def object_created(sender, instance, created, *args, **kwargs):
    if created:
        ObjectAction.objects.create(
                user=instance.owner,
                action_type="created",
                content_type=ContentType.objects.get_for_model(sender),
                object_id=instance.id)

@receiver(pre_delete,sender=Car)
def object_deleted(sender, instance, *args, **kwargs):
    if instance:
        ObjectAction.objects.create(
                action_type="deleted",
                content_type=ContentType.objects.get_for_model(sender),
                object_id=instance.id)