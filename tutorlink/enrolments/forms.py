from django import forms
from .models import EnrolmentRequest

class EnrolmentRequestForm(forms.ModelForm):
    class Meta:
        model = EnrolmentRequest
        fields = ['child', 'start_date', 'message']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, children=None, **kwargs):
        super().__init__(*args, **kwargs)
        if children is not None:
            self.fields['child'].queryset = children

        
        
            
        