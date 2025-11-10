# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .models import SkillProfile, ExchangeRequest
from django.db import transaction

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        teach_skill = request.POST.get('teach_skill', '').strip()
        learn_skill = request.POST.get('learn_skill', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            SkillProfile.objects.create(user=user, teach_skill=teach_skill, learn_skill=learn_skill)

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('login')

        user = authenticate(username=user_obj.username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid password.")
            return redirect('login')

    return render(request, 'login.html')



@login_required
def home_view(request):
    user = request.user
    try:
        user_profile = SkillProfile.objects.get(user=user)
    except SkillProfile.DoesNotExist:
        user_profile = None

    return render(request, 'home.html', {'user_profile': user_profile})


@login_required
def find_matches(request):
    # Ensure the user has a profile
    user = request.user
    try:
        user_profile = SkillProfile.objects.get(user=user)
    except SkillProfile.DoesNotExist:
        messages.warning(request, "Please set your teach/learn skills in your profile.")
        return render(request, 'matches.html', {'matches': [], 'user_profile': None})

    matches = SkillProfile.objects.filter(
        teach_skill__iexact=user_profile.learn_skill,
        learn_skill__iexact=user_profile.teach_skill
    ).exclude(user=user)

    return render(request, 'matches.html', {'matches': matches, 'user_profile': user_profile})


@login_required
def send_request(request, receiver_id):
    # Accept both normal POST or AJAX POST (we return JSON for AJAX)
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    receiver = get_object_or_404(User, id=receiver_id)
    if receiver == request.user:
        return JsonResponse({'status': 'error', 'message': "Can't send request to yourself."}, status=400)

    existing = ExchangeRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').first()
    if existing:
        # if AJAX, return JSON; else redirect with message
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'exists', 'message': 'Request already pending.'})
        messages.info(request, "Request already pending.")
        return redirect('find_matches')

    req = ExchangeRequest.objects.create(sender=request.user, receiver=receiver)
    # AJAX -> JSON success; normal POST -> redirect and flash message
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'message': f'Connection request sent to {receiver.username}.'})
    messages.success(request, f"Connection request sent to {receiver.username}.")
    return redirect('find_matches')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import ExchangeRequest

@login_required
def requests_page(request):
    # Only show requests sent TO the logged-in user
    user_requests = ExchangeRequest.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'requests.html', {'requests': user_requests})



@login_required
def accept_request(request, request_id):
    req = get_object_or_404(ExchangeRequest, id=request_id, receiver=request.user)
    req.status = 'accepted'
    req.save()
    return redirect('requests_page')

@login_required
def reject_request(request, request_id):
    req = get_object_or_404(ExchangeRequest, id=request_id, receiver=request.user)
    req.status = 'rejected'
    req.save()
    return redirect('requests_page')





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import models
from .models import ExchangeRequest, Chat
from django.contrib.auth.models import User

@login_required
def chat_view(request):
    # Find accepted connection
    connection = ExchangeRequest.objects.filter(
        (models.Q(sender=request.user) | models.Q(receiver=request.user)),
        status='accepted'
    ).first()

    if not connection:
        return render(request, "chat.html", {"no_match": True})

    # Identify the connected user
    other_user = connection.receiver if connection.sender == request.user else connection.sender

    # ✅ If message is sent
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text.strip():
            Chat.objects.create(
                sender=request.user,
                receiver=other_user,
                message=message_text.strip()
            )
        return redirect("chat")  # refresh to show new message

    # ✅ Load message history
    messages = Chat.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    return render(request, "chat.html", {
        "other_user": other_user,
        "messages": messages,
    })
    
    
    
    
 # myapp/views.py (add these functions near other views)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SkillProfile, ExchangeRequest

from django.contrib.auth.models import User
from django.db.models import Avg, Q

def _has_accepted_connection(user_a, user_b):
    """Return True if there's an accepted ExchangeRequest between user_a and user_b."""
    return ExchangeRequest.objects.filter(
        (Q(sender=user_a) & Q(receiver=user_b) | Q(sender=user_b) & Q(receiver=user_a)),
        status='accepted'
    ).exists()




# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Avg, Q
from django.contrib.auth.models import User

from .models import SkillProfile, ExchangeRequest, Review
from .forms import EditProfileForm, ReviewForm

@login_required
def profile_view(request, user_id):
    # show profile for user with id=user_id
    profile_user = get_object_or_404(User, id=user_id)
    # ensure SkillProfile exists (signals create it on user creation but just in case)
    skill_profile, _ = SkillProfile.objects.get_or_create(user=profile_user)

    # reviews about this user
    reviews = Review.objects.filter(reviewed=profile_user).select_related('reviewer')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # can the current user submit a review about this profile_user?
    can_review = False
    if request.user != profile_user:
        # they must be connected via an accepted ExchangeRequest (either direction)
        accepted = ExchangeRequest.objects.filter(
            (Q(sender=request.user) & Q(receiver=profile_user)) |
            (Q(sender=profile_user) & Q(receiver=request.user)),
            status='accepted'
        ).exists()
        can_review = accepted

    context = {
        'profile_user': profile_user,
        'user_profile': skill_profile,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 2) if avg_rating else 0,
        'can_review': can_review,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    # edit current user's profile and email
    skill_profile, _ = SkillProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=skill_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(reverse('profile', kwargs={'user_id': request.user.id}))
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EditProfileForm(instance=skill_profile, user=request.user)
    return render(request, 'edit_profile.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Review, ExchangeRequest
from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import ExchangeRequest, Review


@login_required
def review_page(request):
    # ✅ Fetch all accepted connection users
    accepted_users = set()

    accepted_sent = ExchangeRequest.objects.filter(
        sender=request.user, status='accepted'
    )
    accepted_received = ExchangeRequest.objects.filter(
        receiver=request.user, status='accepted'
    )

    for req in accepted_sent:
        accepted_users.add(req.receiver)
    for req in accepted_received:
        accepted_users.add(req.sender)

    if request.method == "POST":
        reviewed_id = request.POST.get("reviewed_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if reviewed_id and rating and comment:
            reviewed_user = User.objects.get(id=reviewed_id)

            # ✅ If already reviewed → update review
            existing_review = Review.objects.filter(
                reviewer=request.user,
                reviewed=reviewed_user
            ).first()

            if existing_review:
                existing_review.rating = rating
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, "✅ Review updated successfully!")
            else:
                Review.objects.create(
                    reviewer=request.user,
                    reviewed=reviewed_user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, "✅ Review submitted successfully!")
        else:
            messages.error(request, "⚠️ All fields are required!")

    return render(request, "review.html", {
        "connected_users": accepted_users,
        "stars": [1, 2, 3, 4, 5]  # ⭐ Left → Right star order
    })






    
    
    
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def logout_confirm(request):
    return render(request, "logout.html")

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect("login")  # Change to your login page name



from django.shortcuts import render
from .models import Job

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'job_list.html', {'jobs': jobs})



from django.shortcuts import render
from .models import Skill

def skills(request):
    all_skills = Skill.objects.all()
    return render(request, 'skills.html', {'skills': all_skills})






