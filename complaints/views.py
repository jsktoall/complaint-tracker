from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.template import loader

from .models import Complaint
from .forms import ComplaintForm, SolveComplaintForm



def home(request):
    return render(request, 'complaints/home.html')

@csrf_exempt
def register_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/register.html', {'form': form})

from django.shortcuts import get_object_or_404
from .forms import SolveComplaintForm

from datetime import date

def unsolved_complaints(request):
    complaints = Complaint.objects.filter(is_solved=False)
    for c in complaints:
        c.days_since = (date.today() - c.date_received).days
    return render(request, 'complaints/unsolved.html', {'complaints': complaints})

def solved_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = SolveComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            solved = form.save(commit=False)
            solved.is_solved = True
            solved.date_solved = timezone.now()
            solved.save()
            return redirect('unsolved_complaints')
    else:
        form = SolveComplaintForm(instance=complaint)
    return render(request, 'complaints/solved.html', {'form': form, 'complaint': complaint})
from django.utils import timezone
from django.template import loader

def solved_complaints(request):
    complaints = Complaint.objects.filter(is_solved=True)
    return render(request, 'complaints/solved_complaints.html', {'complaints': complaints})


def confirm_solve(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if request.method == 'POST':
        solution = request.POST.get('solution_details')
        complaint.solution_details = solution
        complaint.solved_by = "Technician Name"  # Replace with logged-in user later
        complaint.is_solved = True
        complaint.date_solved = timezone.now()
        complaint.save()
        return redirect('unsolved_complaints')
    return render(request, 'complaints/confirm_solve.html', {'complaint': complaint})

def mark_solved(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    complaint.is_solved = True
    complaint.date_solved = timezone.now()
    complaint.solved_by = "You"  # You can update this dynamically later
    complaint.solution_details = "Marked as solved."  # Optional
    complaint.save()
    return redirect('unsolved_complaints')

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now, timedelta
from .models import Complaint

def is_admin(user):
    return user.is_superuser  # or use user.groups.filter(name='Admins').exists() for group-based

@user_passes_test(is_admin)
def export_report(request):
    # Read filter from query param
    period = request.GET.get('period', 'weekly')
    today = now().date()

    if period == 'monthly':
        start_date = today.replace(day=1)
    else:  # default to weekly
        start_date = today - timedelta(days=7)

    complaints = Complaint.objects.filter(date_received__gte=start_date)

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="complaints_{period}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Complaint No', 'Date Received', 'House Name', 'Received From', 'Forwarded To',
        'Complaint 1', 'Complaint 2', 'Complaint 3', 'Complaint 4', 'Complaint 5',
        'Status', 'Date Solved'
    ])

    for c in complaints:
        writer.writerow([
            c.complaint_number, c.date_received, c.house_name, c.received_from, c.forwarded_to,
            c.complaint_1, c.complaint_2, c.complaint_3, c.complaint_4, c.complaint_5,
            "Solved" if c.is_solved else "Pending",
            c.date_solved if c.is_solved else "-"
        ])

    return response

from django.http import HttpResponse
import csv
from datetime import timedelta
from django.utils import timezone
from .models import Complaint

def export_complaints(request, period):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    now = timezone.now().date()

    if period == "weekly":
        start_date = now - timedelta(days=7)
    elif period == "monthly":
        start_date = now - timedelta(days=30)
    else:
        return HttpResponse("Invalid period", status=400)

    complaints = Complaint.objects.filter(date_received__gte=start_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="complaints_{period}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Complaint No', 'Date Received', 'From', 'House Name',
        'Complaint 1', 'Complaint 2', 'Complaint 3', 'Complaint 4', 'Complaint 5',
        'Forwarded To', 'Is Solved', 'Date Solved', 'Solved By', 'Solution Details'
    ])

    for c in complaints:
        writer.writerow([
            c.complaint_number, c.date_received, c.received_from, c.house_name,
            c.complaint_1, c.complaint_2, c.complaint_3, c.complaint_4, c.complaint_5,
            c.forwarded_to, c.is_solved, c.date_solved, c.solved_by, c.solution_details
        ])

    return response


