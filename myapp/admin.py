from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, AgencyDetail

# Register your models here
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency_name', 'phone_number')

@admin.register(AgencyDetail)
class AgencyDetailAdmin(admin.ModelAdmin):
    list_display = ('agency', 'accepting_referrals', 'last_updated')
    list_filter = ('accepting_referrals', 'last_updated')
