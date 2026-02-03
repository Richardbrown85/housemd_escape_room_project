from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from .models import Booking

class BookingForm(forms.ModelForm):
    TIME_SLOT_CHOICES = [
        ('', '-- Select a time --'),
        ('14:00', '2:00 PM'),
        ('16:00', '4:00 PM'),
        ('18:00', '6:00 PM'),
        ('20:00', '8:00 PM'),
    ]

    time = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Time'
    )

    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'date', 'time', 'number_of_people']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(555) 123-4567'}),
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

    def clean_time(self):
        """Convert the string choice back to a time object for the model"""
        from datetime import time as dt_time
        time_str = self.cleaned_data.get('time')
        if time_str:
            hour, minute = map(int, time_str.split(':'))
            return dt_time(hour, minute)
        raise ValidationError("Please select a time slot.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select the current time when editing an existing booking
        if self.instance.pk and self.instance.time:
            self.fields['time'].initial = self.instance.time.strftime('%H:%M')
    
    def clean_date(self):
        """Validate that booking date is not in the past"""
        booking_date = self.cleaned_data.get('date')
        if booking_date and booking_date < date.today():
            raise ValidationError("Booking date cannot be in the past.")
        return booking_date
    
    def clean_number_of_people(self):
        """Validate number of people"""
        number = self.cleaned_data.get('number_of_people')
        if number and number < 1:
            raise ValidationError("At least 1 person is required.")
        if number and number > 10:
            raise ValidationError("Maximum 10 people per booking.")
        return number
    
    def clean(self):
        """Check for double booking"""
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        booking_time = cleaned_data.get('time')
        
        if booking_date and booking_time:
            existing_bookings = Booking.objects.filter(
                date=booking_date,
                time=booking_time,
                status__in=['pending', 'confirmed']
            )
            
            # Exclude current instance when editing
            if self.instance.pk:
                existing_bookings = existing_bookings.exclude(pk=self.instance.pk)
            
            if existing_bookings.exists():
                raise ValidationError(
                    "This time slot is already booked. Please choose another time."
                )
        
        return cleaned_data


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class BookingSearchForm(forms.Form):
    """Form for searching and filtering bookings"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by order number, name, or email...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Booking.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='To Date'
    )