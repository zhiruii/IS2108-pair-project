from accounts.forms import UserProfileForm
from django import forms

class AdminUserForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = UserProfileForm.Meta.fields + ['is_active']

class DisputeResolveForm(forms.Form):
    DECISION_CHOICES = [
        ('UPHOLD', 'Uphold: remove the rating'),
        ('REJECT', 'Reject: keep the rating'),
    ]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect)
    admin_note = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
