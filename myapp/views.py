import logging
import json
from django.utils.timezone import now  # For timezone-aware datetime stamps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignUpForm
from .models import Profile, AgencyDetail, Service
from django.db import models

# Set up logging
logger = logging.getLogger(__name__)


# Login View
def login_view(request):
    """
    Handles user login.
    """
    logger.info("Login view accessed.")
    form = LoginForm(request, data=request.POST) if request.method == 'POST' else LoginForm()

    if request.method == 'POST':
        logger.debug(f"Processing POST request for login: {request.POST}")
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User {user.username} logged in successfully.")
            return redirect('dashboard')  # Redirect to dashboard
        else:
            logger.warning("Invalid login attempt.")
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'myapp/login.html', {'form': form})


# Logout View
def logout_view(request):
    """
    Logs out the currently logged-in user.
    """
    logger.info(f"User {request.user.username} logging out.")
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# Dashboard View (Protected - Requires Login)
@login_required
def dashboard_view(request):
    """
    Displays a list of agencies, filtered based on referral status if applicable.
    """
    logger.info(f"Dashboard view accessed by user: {request.user.username}.")

    # Fetch agencies along with related agency details
    agencies = Profile.objects.prefetch_related('user__agency_details').order_by("agency_name")

    # Filter agencies based on "accepting referrals" status if provided
    accepting_referrals = request.GET.get('accepting_referrals', '').lower()

    # Annotate the Profile queryset with the `accepting_referrals` field from the related AgencyDetail
    agencies = agencies.annotate(accepting_referrals=models.F('user__agency_details__accepting_referrals'))

    if accepting_referrals == 'yes':
        agencies = agencies.filter(accepting_referrals=True)
        logger.info("Filtered agencies accepting referrals.")
    elif accepting_referrals == 'no':
        agencies = agencies.filter(accepting_referrals=False)
        logger.info("Filtered agencies NOT accepting referrals.")

    return render(request, 'myapp/dashboard.html', {'agencies': agencies})


# API: Get or Update Agency Details (AJAX Call)
@login_required
def agency_details(request, agency_id):
    """
    API View to fetch or update the agency details.
    Includes phone number, email, referrals, services, and last updated info.
    """
    logger.info(f"Agency details access by user {request.user.username} for agency ID {agency_id}.")

    # Fetch agency and its details
    agency = get_object_or_404(Profile, id=agency_id)
    agency_detail, created = AgencyDetail.objects.get_or_create(agency=agency.user)

    if request.method == "GET":
        # Fetch all services for the dropdown
        all_services = Service.objects.all()

        # Prepare response data
        data = {
            "agency_name": agency.agency_name or "N/A",  # Fallback to "N/A" if no name is provided
            "phone_number": agency.phone_number or "N/A",  # Fallback to "N/A"
            "email": agency.user.email or "N/A",  # Fallback to "N/A"
            "accepting_referrals": agency_detail.accepting_referrals,
            "referral_limit": agency_detail.referral_limit,
            "services_provided": [service.key for service in agency_detail.services_provided.all()],
            "available_services": [{"key": s.key, "name": s.name} for s in all_services],
            "last_updated": agency_detail.last_updated.strftime(
                "%m/%d/%Y") if agency_detail.last_updated else "Never Updated",
            "is_owner": request.user == agency.user,  # Determine if the user owns the agency
        }
        logger.info(f"Returning GET response for agency ID {agency_id}.")
        return JsonResponse(data)

    elif request.method == "POST":
        # Ensure only the owner of the agency can update its details
        if request.user != agency.user:
            logger.error(f"Unauthorized update attempt for agency ID {agency_id} by user {request.user.username}.")
            return JsonResponse({"error": "You are not authorized to make changes."}, status=403)

        # Parse the JSON payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload received.")
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        # Update phone number and email if provided
        phone_number = payload.get("phone_number")
        email = payload.get("email")
        if phone_number is not None:
            agency.phone_number = phone_number
        if email is not None:
            agency.user.email = email
            agency.user.save()  # Save changes to the User model

        # Update AgencyDetail fields
        accepting_referrals = payload.get("accepting_referrals")
        referral_limit = payload.get("referral_limit")
        services_provided = payload.get("services_provided", [])

        if accepting_referrals is not None:
            agency_detail.accepting_referrals = accepting_referrals
        if referral_limit is not None:
            agency_detail.referral_limit = int(referral_limit) if accepting_referrals else 0
        agency_detail.services_provided.set(Service.objects.filter(key__in=services_provided))

        # Save changes
        try:
            agency.save()
            agency_detail.save()
            logger.info(f"Agency details updated successfully for agency ID {agency_id}.")
        except Exception as e:
            logger.error(f"Error saving updates for agency ID {agency_id}: {str(e)}")
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

        return JsonResponse({"success": True, "message": "Agency details updated successfully.",
                             "last_updated": agency_detail.last_updated.strftime("%m/%d/%Y")})

    logger.warning("Invalid request method used for agency details API.")
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Sign-Up View
def signup_view(request):
    """
    Handles user registration, creating a Profile linked with the user account.
    """
    logger.info("Signup view accessed.")
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                # Create user and associated profile
                user = form.save()
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "phone_number": form.cleaned_data.get("phone_number", ""),
                        "agency_name": form.cleaned_data.get("agency_name", ""),
                    }
                )
                login(request, user)
                logger.info(f"New user '{user.username}' signed up and logged in.")
                messages.success(request, "Account created successfully! You are now logged in.")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during sign-up process: {str(e)}")
                messages.error(request, f"An unexpected error occurred: {e}")
        else:
            logger.warning(f"Signup validation failed: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'myapp/signup.html', {'form': form})


# Terms of Service View
def terms(request):
    """
    Displays the terms and conditions of the service.
    """
    logger.info("Terms of Service view accessed.")
    return render(request, 'myapp/terms.html')
