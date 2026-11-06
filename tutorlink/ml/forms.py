from django import forms

from accounts.models import LEVEL_CHOICES
from listings.models import Listing
from .models import PriceFlag


class PriceForm(forms.Form):
    subject = forms.ChoiceField(choices=Listing.SUBJECT_CHOICES)
    level = forms.ChoiceField(choices=LEVEL_CHOICES)
    weekday = forms.TypedChoiceField(choices=Listing.WEEKDAY_CHOICES, coerce=int)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    mode = forms.ChoiceField(choices=Listing.MODE_CHOICES)

class FlagForm(forms.ModelForm):
    class Meta:
        model = PriceFlag
        fields = ['note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}
