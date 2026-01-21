from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives  # CHANGED: Use EmailMultiAlternatives
from django.template.loader import render_to_string  # ADDED: For rendering templates
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
            email_sent = send_confirmation_email(booking)  # CHANGED: Capture return value
            
            # UPDATED: Better success message
            if email_sent:
                messages.success(request, f'Booking confirmed! Your order number is {booking.order_number}. A confirmation email has been sent to {booking.email}')
            else:
                messages.success(request, f'Booking confirmed! Your order number is {booking.order_number}.')
                messages.warning(request, 'There was an issue sending the confirmation email. Please check your spam folder or contact us.')
            
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
    """
    Send booking confirmation email with HTML template
    
    COMPLETELY UPDATED FUNCTION
    """
    subject = f'Booking Confirmed - Order #{booking.order_number} - House M.D. Escape Room'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [booking.email]
    
    # Prepare context for email templates
    context = {
        'booking': booking
    }
    
    try:
        # Render HTML email template
        html_content = render_to_string('emails/booking_confirmation.html', context)
        
        # Render plain text email template (fallback)
        text_content = render_to_string('emails/booking_confirmation.txt', context)
        
        # Create email with both HTML and plain text versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,  # Plain text version
            from_email=from_email,
            to=to_email
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        print(f"✓ Confirmation email sent successfully to {booking.email}")
        return True
        
    except Exception as e:
        print(f"✗ Error sending confirmation email to {booking.email}: {str(e)}")
        return False