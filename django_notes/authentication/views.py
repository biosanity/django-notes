from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

from django_notes import settings

# Create your views here.
def home(request):
    return render(request, 'authentication/index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        verifypassword = request.POST.get('verifypassword')
        
        if User.objects.filter(username=username):
            messages.error(request, "This username already exists.")
            return redirect('home')
        
        if len(username) > 15:
            messages.error(request, "Username must be shorter than 15 characters.")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric.")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "An account already exists with this email address.")
            return redirect('home')
        
        if password != verifypassword:
            messages.error(request, "Passwords do not match, please try again.")
            return redirect('home')
        
        user = User.objects.create_user(username, email, password)
        user.first_name = firstname
        user.last_name = lastname
        user.is_active = False
        user.save()
        
        messages.success(request, "Your account has been created successfully. We have sent you a confirmation email.")
        
        
        current_site = get_current_site(request)
        subject = "Welcome to Django Notes!"
        to_list = [user.email]
        message = render_to_string('confirmation_email.html', {
            'name': user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            to_list
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
    
    return render(request, "authentication/signup.html")
    
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(
                request, 
                'authentication/index.html', 
                {'firstname': firstname}
            )
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('home')
            
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')