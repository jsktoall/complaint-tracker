from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_number', 'date_received', 'house_name', 'is_solved')
