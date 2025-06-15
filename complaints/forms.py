from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'date_received',
            'received_from',
            'house_name',
            'complaint_1',
            'complaint_2',
            'complaint_3',
            'complaint_4',
            'complaint_5',
            'forwarded_to'
        ]
class SolveComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['solved_by', 'solution_details']
