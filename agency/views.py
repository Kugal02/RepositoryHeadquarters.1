from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from collections import defaultdict
from django.core.paginator import Paginator
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas

from .forms import SignUpForm
from .models import UserProfile


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    def form_valid(self, form):
        user = form.get_users().__next__()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': {
                'uid': uid,
                'token': token,
                'reset_url': f"{self.request.scheme}://{self.request.get_host()}/reset/{uid}/{token}/"
            }
        }

        return form.save(**opts)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = user.userprofile
            profile.role = form.cleaned_data['role']
            profile.county = form.cleaned_data['county']
            profile.agency_name = form.cleaned_data['agency_name']
            profile.agency_phone = form.cleaned_data['agency_phone']
            profile.agency_email = form.cleaned_data['agency_email']
            profile.save()

            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    profile = request.user.userprofile
    is_owner = profile.role == 'owner'

    selected_provider = None
    all_providers = UserProfile.objects.filter(role='owner')

    distinct_counties = (
        all_providers
        .values_list('county', flat=True)
        .order_by('county')
        .distinct()
    )

    if provider_id := request.GET.get('provider_id'):
        selected_provider = get_object_or_404(UserProfile, id=provider_id)

    if request.method == 'POST' and is_owner:
        profile.agency_name = request.POST.get('agency_name')
        profile.agency_phone = request.POST.get('agency_phone')
        profile.agency_email = request.POST.get('agency_email')
        profile.referral_status = request.POST.get('referral_status')

        if profile.referral_status == 'accepting':
            profile.residential_referrals = int(request.POST.get('residential_referrals', 0))
            profile.afc_referrals = int(request.POST.get('afc_referrals', 0))
            profile.behavior_referrals = int(request.POST.get('behavior_referrals', 0))
            profile.dsa_facility_referrals = int(request.POST.get('dsa_facility_referrals', 0))
        else:
            profile.residential_referrals = 0
            profile.afc_referrals = 0
            profile.behavior_referrals = 0
            profile.dsa_facility_referrals = 0

        profile.save()
        return redirect('/dashboard/?saved=true')

    return render(request, 'dashboard.html', {
        'profile': profile,
        'is_owner': is_owner,
        'selected_provider': selected_provider,
        'all_providers': all_providers,
        'accepting': profile.referral_status == 'accepting',
        'distinct_counties': distinct_counties,
    })


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@login_required
def state_county_entities(request):
    search_query = request.GET.get('q', '').strip()
    providers = UserProfile.objects.filter(role='owner')

    if search_query:
        providers = providers.filter(
            Q(agency_name__icontains=search_query) |
            Q(county__icontains=search_query)
        )

    providers = providers.order_by('county', 'agency_name')

    paginator = Paginator(providers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    distinct_counties = (
        UserProfile.objects.filter(role='owner')
        .values_list('county', flat=True)
        .order_by('county')
        .distinct()
    )

    return render(request, 'state_county_entities.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'distinct_counties': distinct_counties,
    })


def export_csv(request):
    providers = UserProfile.objects.filter(role='owner').order_by('county', 'agency_name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="state_county_entities.csv"'

    writer = csv.writer(response)
    writer.writerow(['County', 'Agency Name', 'Phone', 'Email'])

    for provider in providers:
        writer.writerow([provider.county, provider.agency_name, provider.agency_phone, provider.agency_email])

    return response


def export_pdf(request):
    providers = UserProfile.objects.filter(role='owner').order_by('county', 'agency_name')

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "State/County Entities")
    y -= 30

    p.setFont("Helvetica", 10)
    for provider in providers:
        line = f"{provider.county} - {provider.agency_name}, {provider.agency_phone}, {provider.agency_email}"
        p.drawString(40, y, line)
        y -= 15
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="state_county_entities.pdf"'
    return response