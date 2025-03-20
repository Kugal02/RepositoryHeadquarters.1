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
    # Fetch agencies ordered alphabetically by name
    agencies = Profile.objects.all().order_by("agency_name")

    # Filter agencies based on "accepting referrals" status if provided
    accepting_referrals = request.GET.get('accepting_referrals', '').lower()
    if accepting_referrals == 'yes':
        agencies = agencies.filter(agency_details__accepting_referrals=True)
        logger.info("Filtered agencies accepting referrals.")
    elif accepting_referrals == 'no':
        agencies = agencies.filter(agency_details__accepting_referrals=False)
        logger.info("Filtered agencies NOT accepting referrals.")

    return render(request, 'myapp/dashboard.html', {'agencies': agencies})


# API: Get or Update Agency Details (AJAX Call)
@login_required
def agency_details(request, agency_id):
    """
    API View to fetch or update the agency details.
    """
    agency = get_object_or_404(Profile, id=agency_id)
    agency_detail, created = AgencyDetail.objects.get_or_create(agency=agency.user)

    if request.method == "GET":
        all_services = Service.objects.all()
        data = {
            "agency_name": agency.agency_name,
            "accepting_referrals": agency_detail.accepting_referrals,
            "referral_limit": agency_detail.referral_limit,
            "services_provided": [service.key for service in agency_detail.services_provided.all()],
            "available_services": [{"key": s.key, "name": s.name} for s in all_services],
            "last_updated": agency_detail.last_updated.strftime("%m/%d/%Y"),
            "is_owner": (request.user == agency.user),
        }
        return JsonResponse(data)

    elif request.method == "POST":
        if request.user != agency.user:
            return JsonResponse({"error": "You are not authorized to make changes."}, status=403)

        payload = json.loads(request.body)
        agency_detail.accepting_referrals = payload.get("accepting_referrals", False)
        agency_detail.referral_limit = payload.get("referral_limit", 0) if agency_detail.accepting_referrals else 0
        agency_detail.services_provided.set(Service.objects.filter(key__in=payload.get("services_provided", [])))
        agency_detail.save()
        return JsonResponse({"success": True, "last_updated": agency_detail.last_updated.strftime("%m/%d/%Y")})

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
