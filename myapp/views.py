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
    form = LoginForm(request, data=request.POST) if request.method == 'POST' else LoginForm()

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'myapp/login.html', {'form': form})


# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# Dashboard View (Protected - Requires Login)
@login_required
def dashboard_view(request):
    """
    Fetches the list of agencies and filters them based on the referral status if applicable.
    Only profiles that belong to existing users are displayed.
    """
    agencies = Profile.objects.all().order_by("agency_name")  # Fetch agencies in alphabetical order

    # Filter agencies based on accepting referrals status
    accepting_referrals = request.GET.get('accepting_referrals', '')
    if accepting_referrals:
        agencies = agencies.filter(agency_details__accepting_referrals=(accepting_referrals.lower() == 'yes'))

    return render(request, 'myapp/dashboard.html', {'agencies': agencies})


# API: Get or Update Agency Details (AJAX Call)
@login_required
def agency_details(request, agency_id):
    """
    Handles fetching and updating agency details.
    All users can view details via GET, but only the owner can update details via POST.
    """
    logger.info(f"Received request for agency ID: {agency_id}")

    try:
        # Get profile corresponding to the agency
        agency = get_object_or_404(Profile, id=agency_id)

        # Ensure AgencyDetail exists
        agency_detail, created = AgencyDetail.objects.get_or_create(agency=agency.user)

        # Handle GET request (fetch agency details)
        if request.method == "GET":
            data = {
                "agency_name": agency.agency_name or "No Name Provided",
                "accepting_referrals": agency_detail.accepting_referrals,
                "referral_limit": agency_detail.referral_limit or 0,  # Default limit to 0
                "services_provided": [
                    service.name for service in agency_detail.services_provided.all()
                ],
                "last_updated": (
                    agency_detail.last_updated.strftime("%m/%d/%Y")
                    if agency_detail.last_updated else "Never Updated"
                ),
                "is_owner": agency.user == request.user,  # Permissions check
            }
            logger.info(f"Agency details fetched successfully for agency ID {agency_id}")
            return JsonResponse(data)

        # Handle POST request (update details)
        elif request.method == "POST":
            if agency.user != request.user:
                logger.warning(f"Unauthorized update attempt by user {request.user.username} on agency ID {agency_id}")
                return JsonResponse({"error": "You are not authorized to update this agency."}, status=403)

            try:
                # Parse JSON body
                payload = json.loads(request.body)
                accepting_referrals = payload.get("accepting_referrals", False)
                referral_limit = payload.get("referral_limit", 0)
                services_ids = payload.get("services_provided", [])

                # Update fields and set `last_updated`
                agency_detail.accepting_referrals = accepting_referrals
                agency_detail.referral_limit = min(max(referral_limit, 0), 10)  # Enforce bounds
                agency_detail.services_provided.set(
                    Service.objects.filter(id__in=services_ids)
                )
                agency_detail.last_updated = now()  # Update timestamp
                agency_detail.save()

                logger.info(
                    f"Updated details for agency '{agency.agency_name}' by user '{request.user.username}'"
                )

                # Return success response with updated `last_updated`
                return JsonResponse({
                    "success": True,
                    "last_updated": agency_detail.last_updated.strftime("%m/%d/%Y %I:%M %p"),
                })

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON payload for agency ID {agency_id}")
                return JsonResponse({"error": "Invalid data format provided."}, status=400)

            except Exception as e:
                logger.error(f"Error updating agency details for agency ID {agency_id}: {str(e)}")
                return JsonResponse({"error": "Failed to update agency details."}, status=500)

    except Profile.DoesNotExist:
        logger.error(f"Agency Profile with ID {agency_id} does not exist.")
        return JsonResponse({"error": "Agency not found."}, status=404)

    except Exception as e:
        logger.error(f"Error handling request for agency ID {agency_id}: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


# Sign-Up View
def signup_view(request):
    """
    Handles user registration, creating a Profile linked with the user account.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "phone_number": form.cleaned_data.get("phone_number", ""),
                        "agency_name": form.cleaned_data.get("agency_name", ""),
                    }
                )
                login(request, user)
                messages.success(request, "Account created successfully! You are now logged in.")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during sign-up: {str(e)}")
                messages.error(request, f"An unexpected error occurred: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'myapp/signup.html', {'form': form})


# Terms of Service View
def terms(request):
    """
    Displays the terms and conditions of the service.
    """
    return render(request, 'myapp/terms.html')
