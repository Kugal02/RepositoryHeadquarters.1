import json
import re
from io import BytesIO
from datetime import datetime
from collections import defaultdict
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import localtime, now
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit

from accounts.forms import CustomUserSignupForm, CustomLoginForm
from accounts.models import CustomUser
from agency.utils.pdf import generate_coordinator_pdf
from .forms import SignUpForm, UserProfileEditForm, CommunityPostForm, CoordinatorProfileEditForm
from .models import County, Contact, UserProfile, CommunityPost, PostReaction
from datetime import datetime
from .utils.utils import send_mailgun_email
from django.urls import reverse_lazy

def format_phone(phone):
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    return phone


@login_required
def edit_user_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "You do not have a user profile. Please contact an administrator.")
        return redirect('logout')

    contacts = user_profile.contacts.all()

    if request.method == 'POST':
        invalid_contact = False
        submitted_ids = set()

        deleted_ids = request.POST.getlist('deleted_contact_ids')
        if deleted_ids:
            Contact.objects.filter(user_profile=user_profile, id__in=deleted_ids).delete()

        for key in request.POST.keys():
            if key.startswith("contact_first_name_"):
                i = key.split("_")[-1]

                first_name = request.POST.get(f"contact_first_name_{i}")
                last_name = request.POST.get(f"contact_last_name_{i}")
                phone_number = format_phone(request.POST.get(f"contact_phone_number_{i}"))
                email = request.POST.get(f"contact_email_{i}")
                address = request.POST.get(f"contact_address_{i}")
                contact_type = request.POST.get(f"contact_type_{i}")
                other_service_desc = request.POST.get(f"contact_other_service_desc_{i}")
                contact_id = request.POST.get(f"contact_id_{i}")

                if not first_name or not last_name:
                    invalid_contact = True
                    break

                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id, user_profile=user_profile)
                        contact.first_name = first_name
                        contact.last_name = last_name
                        contact.phone_number = phone_number
                        contact.email = email
                        contact.address = address
                        contact.contact_type = contact_type
                        contact.other_service_desc = other_service_desc
                        contact.save()
                        submitted_ids.add(contact.id)
                    except Contact.DoesNotExist:
                        contact = Contact.objects.create(
                            user_profile=user_profile,
                            first_name=first_name,
                            last_name=last_name,
                            phone_number=phone_number,
                            email=email,
                            address=address,
                            contact_type=contact_type,
                            other_service_desc=other_service_desc
                        )
                        submitted_ids.add(contact.id)
                else:
                    contact = Contact.objects.create(
                        user_profile=user_profile,
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        email=email,
                        address=address,
                        contact_type=contact_type,
                        other_service_desc=other_service_desc
                    )
                    submitted_ids.add(contact.id)

        if invalid_contact:
            messages.error(request, "First Name and Last Name are required for all contacts.")
            return redirect('edit_profile')

        form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)

        for key in list(form.errors):
            if key.startswith('contact_'):
                del form.errors[key]

        if form.is_valid():
            form.save()
            return redirect(f"{reverse('dashboard')}?provider_id={user_profile.id}")
        else:
            messages.error(request, "There was an error updating the profile.")

    else:
        form = UserProfileEditForm(instance=user_profile)
        if not contacts.exists():
            contacts = [None]

    return render(request, 'agency/edit_profile.html', {'form': form, 'contacts': contacts})


@login_required
def community_post_create_view(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user.userprofile
            post.save()
            messages.success(request, "Your post has been created!")

            # 🌟 Determine provider ID if applicable
            profile_id = request.user.userprofile.id
            if request.user.userprofile.role == 'provider':
                return redirect(f"{reverse('dashboard')}?provider_id={profile_id}")
            else:
                return redirect('dashboard')  # coordinator

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CommunityPostForm()

    return render(request, 'community/post_create.html', {'form': form})


@login_required
def community_post_list_view(request):
    post_type_filter = request.GET.get('type', '')
    county_filter = request.GET.get('county', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    posts = CommunityPost.objects.all().order_by('-created_at')

    if post_type_filter:
        posts = posts.filter(post_type=post_type_filter)

    if county_filter:
        posts = posts.filter(county__id=county_filter)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            posts = posts.filter(event_date__gte=start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            posts = posts.filter(event_date__lte=end)
        except ValueError:
            pass

    counties = County.objects.all().order_by('name')
    emojis = ['🎉', '❤️', '👍']

    # Count of emoji reactions per post
    reaction_counts = defaultdict(dict)
    # Whether the current user has reacted with each emoji
    reaction_data = defaultdict(dict)

    for post in posts:
        for emoji in emojis:
            reaction_counts[post.id][emoji] = post.reactions.filter(emoji=emoji).count()
            reaction_data[post.id][emoji] = post.reactions.filter(user=request.user, emoji=emoji).exists()

    return render(request, 'community/post_list.html', {
        'posts': posts,
        'counties': counties,
        'selected_type': post_type_filter,
        'selected_county': county_filter,
        'start_date': start_date,
        'end_date': end_date,
        'reaction_emojis': emojis,
        'reaction_counts': dict(reaction_counts),
        'reaction_data': dict(reaction_data),
    })

# View to update referrals
def update_referral(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        referral_type = data.get('referral_type')
        new_value = data.get('new_value')

        try:
            new_value = int(new_value)
        except ValueError:
            return JsonResponse({"error": "Invalid value."}, status=400)

        user_profile = request.user.userprofile

        if hasattr(user_profile, referral_type):
            setattr(user_profile, referral_type, new_value)
            user_profile.save()
            return JsonResponse({"success": "Referral updated successfully."})
        else:
            return JsonResponse({"error": "Invalid referral field."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# View to update referral status
@require_POST
@csrf_exempt
def update_referral_status(request):
    try:
        data = json.loads(request.body)
        referral_status = data.get('referral_status')

        if referral_status not in ['accepting', 'not_accepting']:
            return JsonResponse({"error": "Invalid referral status"}, status=400)

        user_profile = request.user.userprofile
        user_profile.referral_status = referral_status

        if referral_status == 'not_accepting':
            user_profile.residential_referrals = 0
            user_profile.afc_referrals = 0
            user_profile.behavior_referrals = 0
            user_profile.dsa_facility_referrals = 0
            user_profile.dsa_community_referrals = 0
            user_profile.dsa_community_solo_referrals = 0
            user_profile.vocational_rehabilitation_referrals = 0
            user_profile.career_exploration_referrals = 0
            user_profile.job_development_referrals = 0
            user_profile.job_coaching_referrals = 0
            user_profile.job_search_assistance_referrals = 0
            user_profile.employment_path_community_referrals = 0
            user_profile.employment_path_community_solo_referrals = 0
            user_profile.adl_iadl_referrals = 0

        user_profile.save()

        return JsonResponse({
            "success": True,
            "referral_status": user_profile.referral_status,
            "message": "Referral status updated successfully"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Malformed JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Password reset view
class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')  # Redirect after success

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = form.get_users(email).__next__()

        # Generate the UID and token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Create the reset URL
        reset_url = f"{self.request.scheme}://{self.request.get_host()}/reset/{uid}/{token}/"

        # Prepare the subject and message
        subject = "Password Reset for Your ProviderAgencyPortal.com Account"
        message = render_to_string(self.email_template_name, {
            'user': user,
            'reset_url': reset_url,
            'year': datetime.now().year,
        })

        # Use the send_mailgun_email function to send the email
        if send_mailgun_email(subject, message, email):
            return super().form_valid(form)  # Proceed with the normal flow
        else:
            return JsonResponse({"error": "Failed to send reset email"}, status=500)


# Dashboard view
# Safety Redirect: If the user is a coordinator and provider_id is in the URL, remove it.
def dashboard(request):
    user_profile = request.user.userprofile
    provider_id = request.GET.get('provider_id')

    # Safety redirect for coordinators: Remove the provider_id from URL
    if user_profile.role == 'coordinator' and provider_id == str(user_profile.id):
        return redirect('dashboard')

    referral_status_filter = request.GET.get('referral_status', '')
    county_filter = request.GET.get('county')
    selected_service = request.GET.get('service_filter')

    selected_provider = None
    last_login_display = None
    last_login_status = None

    all_providers = UserProfile.objects.filter(
        role='provider',
        user__is_superuser=False
    ).order_by('user__display_name')

    # Apply filters
    if referral_status_filter:
        all_providers = all_providers.filter(referral_status=referral_status_filter)

    if county_filter and county_filter.strip():
        all_providers = all_providers.filter(counties__id=county_filter)
    else:
        county_filter = ''

    if selected_service:
        all_providers = all_providers.filter(**{selected_service: True})

    # Handle selected provider
    if provider_id:
        try:
            selected_provider = UserProfile.objects.get(id=provider_id)

            if selected_provider.user.last_login:
                pacific_login_time = localtime(selected_provider.user.last_login)
                last_login_display = pacific_login_time.strftime("%m/%d/%Y %I:%M%p").lower()
                days_since = (localtime(now()) - pacific_login_time).days
                last_login_status = "old" if days_since >= 4 else "recent"

            if user_profile.role == 'coordinator' and selected_provider.id == user_profile.id:
                selected_provider = None

        except UserProfile.DoesNotExist:
            messages.error(request, "The selected provider does not exist.")
            selected_provider = None
    else:
        if user_profile.role == 'provider':
            selected_provider = user_profile

    service_choices = [
        ('residential_referrals', 'Residential Services'),
        ('afc_referrals', 'Adult Foster Care'),
        ('behavior_referrals', 'Behavior Services'),
        ('dsa_facility_referrals', 'DSA Facility'),
        ('dsa_community_referrals', 'DSA Community'),
        ('dsa_community_solo_referrals', 'DSA Community Solo'),
        ('vocational_rehabilitation_referrals', 'Vocational Rehabilitation'),
        ('career_exploration_referrals', 'Career Exploration'),
        ('job_development_referrals', 'Job Development'),
        ('job_coaching_referrals', 'Job Coaching'),
        ('job_search_assistance_referrals', 'Job Search Assistance'),
        ('employment_path_community_referrals', 'Employment Path Community'),
        ('employment_path_community_solo_referrals', 'Employment Path Community Solo'),
        ('adl_iadl_referrals', 'ADL/IADL Services'),
    ]

    distinct_counties = County.objects.filter(userprofile__role='provider').distinct()
    contacts = selected_provider.contacts.all() if selected_provider else []

    return render(request, 'dashboard.html', {
        'profile': user_profile,
        'all_providers': all_providers,
        'selected_provider': selected_provider,
        'distinct_counties': distinct_counties,
        'accepting': user_profile.referral_status == 'accepting',
        'referral_status_filter': referral_status_filter,
        'selected_county': county_filter,
        'last_login_display': last_login_display,
        'last_login_status': last_login_status,
        'contacts': contacts,
        'selected_service': selected_service,
        'service_choices': service_choices,
        'coordinator_message': (
            "Click on a provider agency to view their agency information."
            if user_profile.role == 'coordinator' and not provider_id else None
        )
    })


# Export PDF view
def export_pdf(request):
    search_query = request.GET.get('q', '').strip()
    selected_entity_type = request.GET.get('entity_type', '')

    coordinators = UserProfile.objects.filter(role='coordinator')

    if search_query:
        coordinators = coordinators.filter(
            Q(contact_first_name__icontains=search_query) |
            Q(contact_last_name__icontains=search_query)
        )

    if selected_entity_type in ['odds', 'vr']:
        coordinators = coordinators.filter(entity_type=selected_entity_type)

    coordinators = coordinators.prefetch_related('counties').order_by('contact_last_name')

    pdf_buffer = generate_coordinator_pdf(coordinators)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="state_county_directory.pdf"'
    return response


from accounts.forms import CustomLoginForm


def custom_login_view(request):
    if request.method == 'POST':
        print("Login POST data:", request.POST)
        form = CustomLoginForm(request.POST)

        if form.is_valid():
            print("Form is valid")

            user_type = form.cleaned_data['user_type']
            agency_name = form.cleaned_data['agency_name']
            email = form.cleaned_data['username'].strip().lower()
            password = form.cleaned_data['password']

            print("Form values:", user_type, agency_name, email)

            if user_type == 'provider':
                profile = UserProfile.objects.filter(
                    agency_name__iexact=agency_name.strip(),
                    role='provider'
                ).first()

                if not profile:
                    print("No provider profile found")
                    form.add_error(None, f"No provider agency found with the name '{agency_name}'.")
                else:
                    user = profile.user
                    authenticated_user = authenticate(request, username=user.email, password=password)

                    if authenticated_user:
                        auth_login(request, authenticated_user)
                        return redirect(request.GET.get('next') or 'dashboard')
                    else:
                        form.add_error(None, "The password entered is incorrect.")

            elif user_type == 'coordinator':
                user = CustomUser.objects.filter(email__iexact=email).first()

                if not user:
                    form.add_error(None, f"No coordinator account found with email '{email}'.")
                else:
                    authenticated_user = authenticate(request, username=email, password=password)

                    if authenticated_user:
                        if hasattr(authenticated_user, 'userprofile') and authenticated_user.userprofile.role == 'coordinator':
                            auth_login(request, authenticated_user)
                            return redirect(request.GET.get('next') or 'dashboard')
                        else:
                            form.add_error(None, "This email does not belong to a State/County Entity account.")
                    else:
                        form.add_error(None, "The password entered is incorrect.")
        else:
            print("Form is invalid")
            print("Form errors:", form.errors)
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def export_community_posts_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    title = "ProviderAgencyPortal.com - Community Posts"
    y = height - 50

    # Draw blue header
    p.setFillColor(colors.HexColor("#0d6efd"))
    p.rect(0, height - 70, width, 40, fill=1, stroke=0)

    # Centered white header text
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    text_width = p.stringWidth(title, "Helvetica-Bold", 16)
    p.drawString((width - text_width) / 2, height - 55, title)

    y -= 80
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.black)

    posts = CommunityPost.objects.all().order_by('-created_at')
    max_width = width - 100  # Padding for text wrap
    line_height = 14
    x_start = 50

    for post in posts:
        if y < 100:
            p.showPage()
            # Repeat header on new page
            p.setFillColor(colors.HexColor("#0d6efd"))
            p.rect(0, height - 70, width, 40, fill=1, stroke=0)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 16)
            p.drawString((width - text_width) / 2, height - 55, title)
            y = height - 80
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 11)

        p.drawString(x_start, y, f"Title: {post.title}")
        y -= line_height
        p.drawString(x_start, y, f"Type: {post.get_post_type_display()} | County: {post.county.name} | Event Date: {post.event_date.strftime('%b %d, %Y')}")
        y -= line_height
        p.drawString(x_start, y, f"Posted: {post.created_at.strftime('%b %d, %Y')}")
        y -= line_height

        # Wrap and print description
        description_lines = simpleSplit(f"Description: {post.description}", "Helvetica", 11, max_width)
        for line in description_lines:
            p.drawString(x_start, y, line)
            y -= line_height

        y -= 10  # Extra space before next post

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# Home redirect view
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# State and County directory view
def state_county_directory_view(request):
    search_query = request.GET.get('q', '').strip()
    selected_entity_type = request.GET.get('entity_type', '')
    selected_county = request.GET.get('county', '')

    contacts = UserProfile.objects.filter(role='coordinator')

    if search_query:
        contacts = contacts.filter(
            Q(contact_first_name__icontains=search_query) |
            Q(contact_last_name__icontains=search_query)
        )

    if selected_entity_type in ['odds', 'vr']:
        contacts = contacts.filter(entity_type=selected_entity_type)

    if selected_county:
        contacts = contacts.filter(counties__id=selected_county)

    paginator = Paginator(contacts.order_by('contact_last_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    counties = County.objects.all().order_by('name')

    return render(request, 'agency/state_county_directory.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_entity_type': selected_entity_type,
        'selected_county': selected_county,
        'counties': counties,
    })

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, created_by=request.user.userprofile)

    if request.method == 'POST':
        form = CommunityPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('community_post_list')
    else:
        form = CommunityPostForm(instance=post)

    return render(request, 'community/edit_post.html', {
        'form': form,
        'post': post
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, created_by=request.user.userprofile)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('community_post_list')

    return render(request, 'community/delete_post_confirm.html', {
        'post': post
    })

@require_POST
@login_required
def toggle_reaction(request):
    post_id = request.POST.get('post_id')
    emoji = request.POST.get('emoji')

    try:
        post = CommunityPost.objects.get(id=post_id)
    except CommunityPost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    reaction, created = PostReaction.objects.get_or_create(
        post=post,
        user=request.user,
        emoji=emoji
    )

    if not created:
        reaction.delete()
        action = 'removed'
    else:
        action = 'added'

    count = PostReaction.objects.filter(post=post, emoji=emoji).count()

    return JsonResponse({'status': 'ok', 'action': action, 'count': count})


def send_mailgun_email(subject, message, recipient):
    """
    Function to send email using Mailgun API.
    """
    api_url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
    auth = ("api", settings.MAILGUN_API_KEY)  # Basic auth with API key

    # Data payload for Mailgun API request
    data = {
        "from": f"noreply@{settings.MAILGUN_DOMAIN}",
        "to": recipient,
        "subject": subject,
        "text": message,
    }

    # Make the HTTP POST request to Mailgun API
    response = requests.post(api_url, auth=auth, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        return True
    else:
        return False

@login_required
def edit_coordinator_profile(request):
    # Get the logged-in user's profile
    user_profile = request.user.userprofile

    # If the user is a coordinator, show the form
    if user_profile.role != 'coordinator':
        return redirect('dashboard')  # Ensure coordinators are the only ones allowed to edit their profiles

    if request.method == 'POST':
        form = CoordinatorProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to dashboard after saving the form
    else:
        form = CoordinatorProfileEditForm(instance=user_profile)

    return render(request, 'agency/edit_coordinator.html', {'form': form})

# Profile Edit View for Coordinator
@login_required
def edit_coordinator_profile(request):
    user_profile = request.user.userprofile

    # Ensure that only coordinators can access this view
    if user_profile.role != 'coordinator':
        return redirect('state_county_directory')  # Redirect to the state/county directory page if not a coordinator

    if request.method == 'POST':
        form = CoordinatorProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('state_county_directory')  # Redirect to the state/county directory after saving
    else:
        form = CoordinatorProfileEditForm(instance=user_profile)

    return render(request, 'agency/edit_coordinator.html', {'form': form})

def state_county_directory_view(request):
    # Implement the logic to filter and display coordinators, with pagination
    coordinators = UserProfile.objects.filter(role='coordinator')

    # Get query parameters
    search_query = request.GET.get('q', '')
    selected_entity_type = request.GET.get('entity_type', '')
    selected_county = request.GET.get('county', '')

    # Apply filters based on search query, entity type, and county
    if search_query:
        coordinators = coordinators.filter(
            Q(contact_first_name__icontains=search_query) |
            Q(contact_last_name__icontains=search_query)
        )

    if selected_entity_type in ['odds', 'vr']:
        coordinators = coordinators.filter(entity_type=selected_entity_type)

    if selected_county:
        coordinators = coordinators.filter(counties__id=selected_county)

    # Sort coordinators alphabetically by first name, then last name
    coordinators = coordinators.order_by('contact_first_name', 'contact_last_name')

    # Pagination logic
    page_number = request.GET.get('page', 1)
    paginator = Paginator(coordinators, 10)
    page_obj = paginator.get_page(page_number)

    # Get list of counties for the filter dropdown
    counties = County.objects.all().order_by('name')

    # Render the template with filtered, sorted, and paginated coordinators
    return render(request, 'agency/state_county_directory.html', {
        'coordinators': coordinators,
        'search_query': search_query,
        'selected_entity_type': selected_entity_type,
        'selected_county': selected_county,
        'counties': counties,
        'page_obj': page_obj,
    })




