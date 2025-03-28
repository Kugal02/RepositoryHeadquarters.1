from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'Service Coordinator / Personal Agent'),
        ('owner', 'Agency Owner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    county = models.CharField(max_length=100, blank=True)

    # Referral-related fields
    referral_status = models.CharField(
        max_length=20,
        choices=[('accepting', 'Accepting Referrals'), ('not_accepting', 'Not Accepting Referrals')],
        default='not_accepting'
    )
    agency_name = models.CharField(max_length=100, blank=True)
    agency_phone = models.CharField(max_length=20, blank=True)
    agency_email = models.EmailField(blank=True)

    residential_referrals = models.PositiveIntegerField(default=0)
    afc_referrals = models.PositiveIntegerField(default=0)
    behavior_referrals = models.PositiveIntegerField(default=0)
    dsa_facility_referrals = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

