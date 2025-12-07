from django.contrib import admin
from .models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'email', 'date', 'time', 'number_of_people', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['order_number', 'name', 'email']
    date_hierarchy = 'date'