from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking
from .forms import BookingForm, SignUpForm

def home(request):
    return render(request, 'housemd_escape_room/home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'housemd_escape_room/signup.html', {'form': form})

@login_required
def booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Check if slot is available
            existing = Booking.objects.filter(
                date=booking.date,
                time=booking.time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if existing:
                messages.error(request, 'This time slot is already booked. Please choose another.')
                return redirect('booking')
            
            booking.save()
            
            # Send confirmation email
            send_confirmation_email(booking)
            
            messages.success(request, f'Booking confirmed! Your order number is {booking.order_number}')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    
    # Get booked slots for next 30 days
    today = datetime.now().date()
    end_date = today + timedelta(days=30)
    booked_slots = Booking.objects.filter(
        date__gte=today,
        date__lte=end_date,
        status__in=['confirmed', 'pending']
    ).values('date', 'time')
    
    return render(request, 'housemd_escape_room/booking.html', {
        'form': form,
        'booked_slots': list(booked_slots)
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'housemd_escape_room/my_bookings.html', {'bookings': bookings})

def send_confirmation_email(booking):
    subject = f'Booking Confirmation - Order #{booking.order_number}'
    message = f'''
Dear {booking.name},

Your escape room booking has been confirmed!

Order Number: {booking.order_number}
Date: {booking.date}
Time: {booking.time}
Number of People: {booking.number_of_people}

Please arrive 10 minutes early. We look forward to seeing you!

Best regards,
Escape Room Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [booking.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email error: {e}")