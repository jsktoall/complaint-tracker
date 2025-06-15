from django.db import models
from django.utils import timezone

class Complaint(models.Model):
    complaint_number = models.CharField(max_length=20, unique=True, blank=True)
    date_received = models.DateField(default=timezone.now)
    received_from = models.CharField(max_length=100)
    house_name = models.CharField(max_length=100)
    forwarded_to = models.CharField(max_length=100)

    complaint_1 = models.TextField(blank=True, null=True)
    complaint_2 = models.TextField(blank=True, null=True)
    complaint_3 = models.TextField(blank=True, null=True)
    complaint_4 = models.TextField(blank=True, null=True)
    complaint_5 = models.TextField(blank=True, null=True)

    is_solved = models.BooleanField(default=False)
    date_solved = models.DateField(blank=True, null=True)
    solved_by = models.CharField(max_length=100, blank=True, null=True)
    solution_details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.complaint_number:
            last = Complaint.objects.all().order_by('-id').first()
            if last and last.complaint_number:
                last_number = int(last.complaint_number.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.complaint_number = f"CMP-{new_number:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date_received} - {self.house_name}"
