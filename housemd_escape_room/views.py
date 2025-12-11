from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import Booking
from .forms import BookingForm, SignUpForm

def home(request):
    """Homepage view"""
    return render(request, 'housemd_escape_room/home.html')

def signup(request):
    """User signup view"""
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

def booking(request):
    """Booking page with calendar"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Check if user is logged in
            if request.user.is_authenticated:
                booking.user = request.user
                booking.is_guest = False
            else:
                booking.is_guest = True
            
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
            
            messages.success(request, f'Booking confirmed! Your order number is {booking.order_number}. Check your email for details.')
            
            # Redirect based on login status
            if request.user.is_authenticated:
                return redirect('my_bookings')
            else:
                return redirect('booking_confirmation', order_number=booking.order_number)
    else:
        form = BookingForm()
    
    # Get booked slots for next 60 days
    today = datetime.now().date()
    end_date = today + timedelta(days=60)
    booked_slots = Booking.objects.filter(
        date__gte=today,
        date__lte=end_date,
        status__in=['confirmed', 'pending']
    ).values('date', 'time')
    
    # Format for JavaScript
    booked_list = []
    for slot in booked_slots:
        booked_list.append({
            'date': slot['date'].strftime('%Y-%m-%d'),
            'time': slot['time'].strftime('%H:%M')
        })
    
    return render(request, 'housemd_escape_room/booking.html', {
        'form': form,
        'booked_slots': json.dumps(booked_list)
    })

@login_required
def my_bookings(request):
    """View user's bookings"""
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'housemd_escape_room/my_bookings.html', {'bookings': bookings})

def booking_confirmation(request, order_number):
    """Guest booking confirmation page"""
    try:
        booking = Booking.objects.get(order_number=order_number)
        return render(request, 'housemd_escape_room/booking_confirmation.html', {'booking': booking})
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('home')

def send_confirmation_email(booking):
    """Send booking confirmation email"""
    subject = f'Booking Confirmation - Order #{booking.order_number}'
    message = f'''
Dear {booking.name},

Your escape room booking has been confirmed!

Order Number: {booking.order_number}
Date: {booking.date}
Time: {booking.time}
Number of People: {booking.number_of_people}

Please save this email and bring your order number when you arrive.
Arrive 10 minutes early. We look forward to seeing you!

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