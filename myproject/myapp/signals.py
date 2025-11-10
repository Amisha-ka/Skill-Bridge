# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SkillProfile

@receiver(post_save, sender=User)
def create_or_update_skill_profile(sender, instance, created, **kwargs):
    if created:
        SkillProfile.objects.create(user=instance)
    else:
        # ensure a SkillProfile exists for existing users
        SkillProfile.objects.get_or_create(user=instance)
