from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'Service Coordinator / Personal Agent'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    counties = models.ManyToManyField(County, blank=True)

    contact_first_name = models.CharField(max_length=50, null=True, blank=True)
    contact_last_name = models.CharField(max_length=50, default='')
    contact_phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_address = models.CharField(max_length=500, null=True, blank=True)

    referral_status = models.CharField(
        max_length=20,
        choices=[('accepting', 'Accepting Referrals'), ('not_accepting', 'Not Accepting Referrals')],
        default='not_accepting'
    )

    # Boolean flags for each service (indicates if service is provided)
    residential_referrals = models.BooleanField(default=False)
    afc_referrals = models.BooleanField(default=False)
    behavior_referrals = models.BooleanField(default=False)
    dsa_facility_referrals = models.BooleanField(default=False)
    dsa_community_referrals = models.BooleanField(default=False)
    dsa_community_solo_referrals = models.BooleanField(default=False)
    vocational_rehabilitation_referrals = models.BooleanField(default=False)
    career_exploration_referrals = models.BooleanField(default=False)
    job_development_referrals = models.BooleanField(default=False)
    job_coaching_referrals = models.BooleanField(default=False)
    job_search_assistance_referrals = models.BooleanField(default=False)
    employment_path_community_referrals = models.BooleanField(default=False)
    employment_path_community_solo_referrals = models.BooleanField(default=False)
    adl_iadl_referrals = models.BooleanField(default=False)

    # Editable referral count fields (only visible when the service is active and user is accepting referrals)
    residential_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    afc_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    behavior_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_facility_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_community_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_community_solo_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    vocational_rehabilitation_referrals_count = models.PositiveIntegerField(default=0,
                                                                           validators=[MaxValueValidator(99)])
    career_exploration_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_development_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_coaching_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_search_assistance_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    employment_path_community_referrals_count = models.PositiveIntegerField(default=0,
                                                                           validators=[MaxValueValidator(99)])
    employment_path_community_solo_referrals_count = models.PositiveIntegerField(default=0,
                                                                                validators=[MaxValueValidator(99)])
    adl_iadl_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    notes = models.TextField(max_length=500, blank=True, null=True)

    website = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()
