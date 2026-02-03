from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta, date
from .models import Booking
from .forms import BookingForm, SignUpForm, BookingSearchForm
import json

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
            email_sent = send_confirmation_email(booking)
            
            # Success message
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
    bookings = Booking.objects.filter(
        date__gte=today,
        date__lte=end_date,
        status__in=['confirmed', 'pending']
    ).values('date', 'time')
    
    # Convert to JSON-friendly format
    booked_slots = [
        {
            'date': booking['date'].strftime('%Y-%m-%d'),
            'time': booking['time'].strftime('%H:%M')
        }
        for booking in bookings
    ]
    
    # Convert to JSON string
    booked_slots_json = json.dumps(booked_slots)
    
    return render(request, 'housemd_escape_room/booking.html', {
        'form': form,
        'booked_slots': booked_slots_json
    })


# ============================================
# ENHANCED: My Bookings with Search/Filter
# ============================================
@login_required
def my_bookings(request):
    """View user's bookings with search and filter"""
    bookings = Booking.objects.filter(user=request.user)
    
    # Apply filters
    search_form = BookingSearchForm(request.GET)
    
    if search_form.is_valid():
        # Search filter
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            bookings = bookings.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(order_number__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        # Status filter
        status = search_form.cleaned_data.get('status')
        if status:
            bookings = bookings.filter(status=status)
        
        # Date range filter
        date_from = search_form.cleaned_data.get('date_from')
        if date_from:
            bookings = bookings.filter(date__gte=date_from)
        
        date_to = search_form.cleaned_data.get('date_to')
        if date_to:
            bookings = bookings.filter(date__lte=date_to)
    
    # Separate upcoming and past bookings
    today = date.today()
    upcoming_bookings = bookings.filter(date__gte=today).order_by('date', 'time')
    past_bookings = bookings.filter(date__lt=today).order_by('-date', '-time')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'search_form': search_form,
        'total_upcoming': upcoming_bookings.count(),
        'total_past': past_bookings.count(),
        'today': today,
    }
    
    return render(request, 'housemd_escape_room/my_bookings.html', context)


# ============================================
# NEW: View Booking Detail
# ============================================
@login_required
def booking_detail(request, pk):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    # Check if booking can be edited or cancelled
    can_edit = booking.status in ['pending', 'confirmed'] and booking.date >= date.today()
    can_cancel = booking.status in ['pending', 'confirmed'] and booking.date >= date.today()
    
    context = {
        'booking': booking,
        'can_edit': can_edit,
        'can_cancel': can_cancel,
        'is_past': booking.date < date.today(),
    }
    
    return render(request, 'housemd_escape_room/booking_detail.html', context)


# ============================================
# NEW: Edit Booking
# ============================================
@login_required
def edit_booking(request, pk):
    """Edit an existing booking"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    # Check if booking can be edited
    if booking.status == 'cancelled':
        messages.error(request, 'Cannot edit a cancelled booking.')
        return redirect('booking_detail', pk=pk)
    
    if booking.date < date.today():
        messages.error(request, 'Cannot edit past bookings.')
        return redirect('booking_detail', pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            updated_booking = form.save(commit=False)
            updated_booking.user = booking.user
            updated_booking.is_guest = booking.is_guest
            updated_booking.save()
            
            # Send update confirmation email
            email_sent = send_update_email(updated_booking)
            
            if email_sent:
                messages.success(request, f'Booking {booking.order_number} updated successfully! A confirmation email has been sent to {updated_booking.email}.')
            else:
                messages.success(request, f'Booking {booking.order_number} updated successfully!')
                messages.warning(request, 'There was an issue sending the update email. Please check your spam folder or contact us.')
            
            return redirect('booking_detail', pk=booking.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(instance=booking)
    
    return render(request, 'housemd_escape_room/edit_booking.html', {
        'form': form,
        'booking': booking,
    })


# ============================================
# NEW: Cancel Booking
# ============================================
@login_required
def cancel_booking(request, pk):
    """Cancel a booking (soft delete)"""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    # Check if booking can be cancelled
    if booking.status == 'cancelled':
        messages.info(request, 'This booking is already cancelled.')
        return redirect('booking_detail', pk=pk)
    
    if booking.date < date.today():
        messages.error(request, 'Cannot cancel past bookings.')
        return redirect('booking_detail', pk=pk)
    
    if request.method == 'POST':
        # Soft delete - change status to cancelled
        booking.status = 'cancelled'
        booking.save()
        
        # Send cancellation email
        email_sent = send_cancellation_email(booking)
        
        if email_sent:
            messages.success(request, f'Booking {booking.order_number} has been cancelled successfully. A confirmation email has been sent to {booking.email}.')
        else:
            messages.success(request, f'Booking {booking.order_number} has been cancelled successfully.')
            messages.warning(request, 'There was an issue sending the cancellation email. Please check your spam folder or contact us.')
        
        return redirect('my_bookings')
    
    return render(request, 'housemd_escape_room/cancel_booking.html', {
        'booking': booking
    })


# ============================================
# EXISTING: Booking Confirmation (unchanged)
# ============================================
def booking_confirmation(request, order_number):
    """Guest booking confirmation page"""
    try:
        booking = Booking.objects.get(order_number=order_number)
        return render(request, 'housemd_escape_room/booking_confirmation.html', {'booking': booking})
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('home')


# ============================================
# EXISTING: Email Function (unchanged)
# ============================================
def send_confirmation_email(booking):
    """
    Send booking confirmation email with HTML template
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


def send_update_email(booking):
    """
    Send booking update email with HTML template
    """
    subject = f'Booking Updated - Order #{booking.order_number} - House M.D. Escape Room'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [booking.email]
    
    context = {
        'booking': booking
    }
    
    try:
        html_content = render_to_string('emails/booking_update.html', context)
        text_content = render_to_string('emails/booking_update.txt', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        print(f"✓ Update email sent successfully to {booking.email}")
        return True
        
    except Exception as e:
        print(f"✗ Error sending update email to {booking.email}: {str(e)}")
        return False


def send_cancellation_email(booking):
    """
    Send booking cancellation email with HTML template
    """
    subject = f'Booking Cancelled - Order #{booking.order_number} - House M.D. Escape Room'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [booking.email]
    
    context = {
        'booking': booking
    }
    
    try:
        html_content = render_to_string('emails/booking_cancellation.html', context)
        text_content = render_to_string('emails/booking_cancellation.txt', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        print(f"✓ Cancellation email sent successfully to {booking.email}")
        return True
        
    except Exception as e:
        print(f"✗ Error sending cancellation email to {booking.email}: {str(e)}")
        return False