from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from shopping_list.models import ShoppingList

@receiver(post_save, sender=User)
def create_shopping_list(sender, instance, created, **kwargs):
    if created:
        ShoppingList.objects.create(user=instance)