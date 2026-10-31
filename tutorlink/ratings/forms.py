from django import forms
from .models import Rating


class RatingForm(forms.ModelForm):
    stars = forms.TypedChoiceField(
        choices=[('', 'Choose...')] + [(i, i) for i in range(1, 6)],
        coerce=int,
    )


    class Meta:
        model = Rating
        fields = ['stars']
