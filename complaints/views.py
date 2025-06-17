from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta
import csv

from .models import Complaint
from .forms import ComplaintForm, SolveComplaintForm


from django.contrib.auth.models import Group

def is_member(user):
    return user.groups.filter(name='Member').exists()

def is_technician(user):
    return user.groups.filter(name='Technician').exists()

# ---------- HOME ----------
def home(request):
    return render(request, 'complaints/home.html')


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def user_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Invalid username or password"
    return render(request, 'complaints/login.html', {'error': error})

def user_logout(request):
    logout(request)
    return redirect('login')



# ---------- COMPLAINT REGISTRATION (MEMBERS) ----------
@user_passes_test(is_member)
@login_required
def register_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/register.html', {'form': form})


# ---------- VIEW UNSOLVED COMPLAINTS (Everyone) ----------
@login_required
def unsolved_complaints(request):
    complaints = Complaint.objects.filter(is_solved=False)
    for c in complaints:
        c.days_since = (date.today() - c.date_received).days
    return render(request, 'complaints/unsolved.html', {'complaints': complaints})


# ---------- MARK A COMPLAINT AS SOLVED (Technicians) ----------
@user_passes_test(is_technician)
@login_required
def solved_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = SolveComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            solved = form.save(commit=False)
            solved.is_solved = True
            solved.date_solved = timezone.now()
            solved.solved_by = request.user.username
            solved.save()
            return redirect('unsolved_complaints')
    else:
        form = SolveComplaintForm(instance=complaint)
    return render(request, 'complaints/solved.html', {'form': form, 'complaint': complaint})


# ---------- CONFIRMATION SCREEN FOR SOLVING ----------
@user_passes_test(is_technician)
@login_required
def confirm_solve(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if request.method == 'POST':
        solution = request.POST.get('solution_details')
        complaint.solution_details = solution
        complaint.solved_by = request.user.username
        complaint.is_solved = True
        complaint.date_solved = timezone.now()
        complaint.save()
        return redirect('unsolved_complaints')
    return render(request, 'complaints/confirm_solve.html', {'complaint': complaint})


# ---------- QUICK MARK SOLVED WITHOUT FORM (Optional Use) ----------
@login_required
def mark_solved(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.is_solved = True
    complaint.date_solved = timezone.now()
    complaint.solved_by = request.user.username
    complaint.solution_details = "Marked as solved."
    complaint.save()
    return redirect('unsolved_complaints')


# ---------- VIEW SOLVED COMPLAINTS (Everyone) ----------
@login_required
def solved_complaints(request):
    complaints = Complaint.objects.filter(is_solved=True)
    return render(request, 'complaints/solved_complaints.html', {'complaints': complaints})


# ---------- ADMIN CHECK FUNCTION ----------
def is_admin(user):
    return user.is_superuser


# ---------- EXPORT REPORTS (ADMIN ONLY) ----------
@user_passes_test(is_admin)
def export_complaints(request, period):
    now_date = timezone.now().date()

    if period == "weekly":
        start_date = now_date - timedelta(days=7)
    elif period == "monthly":
        start_date = now_date - timedelta(days=30)
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
