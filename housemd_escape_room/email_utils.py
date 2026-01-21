from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to customer
    
    Args:
        booking: Booking model instance
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    subject = f'Booking Confirmed - Order #{booking.order_number} - House M.D. Escape Room'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [booking.email]
    
    # Prepare context for templates
    context = {
        'booking': booking
    }
    
    # Render HTML email
    html_content = render_to_string('emails/booking_confirmation.html', context)
    
    # Render plain text email (fallback)
    text_content = render_to_string('emails/booking_confirmation.txt', context)
    
    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to_email
    )
    
    # Attach HTML version
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        email.send(fail_silently=False)
        print(f"✓ Confirmation email sent to {booking.email}")
        return True
    except Exception as e:
        print(f"✗ Error sending email to {booking.email}: {str(e)}")
        return False