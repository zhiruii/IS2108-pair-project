from django import forms
from .models import Rating, Dispute


class RatingForm(forms.ModelForm):
    stars = forms.TypedChoiceField(
        choices=[('', 'Choose...')] + [(i, i) for i in range(1, 6)],
        coerce=int,
    )


    class Meta:
        model = Rating
        fields = ['stars']

class DisputeForm(forms.ModelForm):
    reason = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 4}))

    class Meta:
        model = Dispute
        fields = ['reason']
