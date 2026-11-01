from datetime import date

from django import forms

class PaymentForm(forms.Form):
    # A plain Form, not a ModelForm: card details are checked but never saved
    name_on_card = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your full name",
            }
        ))
    card_number = forms.CharField(
        min_length=12,
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "placeholder": "1234567812345678",
                "inputmode": "numeric",  # number keypad on phones
                "pattern": "[0-9]{12,19}",  # browser blocks submit if not 12-19 digits
                "title": "12 to 19 digits, no spaces",  # message the browser shows
            }
        ),
    )
    expiry = forms.CharField(
    max_length=5,
    label="Expiry (MM/YY)",
    widget=forms.TextInput(attrs={
        "placeholder": "MM/YY",
        "inputmode": "numeric",
        "pattern": "(0[1-9]|1[0-2])/[0-9]{2}",
        "title": "MM/YY, e.g. 08/28",
        }),
    )
    cvv = forms.CharField(
        min_length=3,
        max_length=3,
        label="CVV",
        widget=forms.TextInput(
            attrs={
                "placeholder": "123",
                "inputmode": "numeric",
                "pattern": "[0-9]{3}",
                "title": "3 digits",
            }
        ),
    )

    def clean_card_number(self):
        number = self.cleaned_data["card_number"]
        if not number.isdigit():
            raise forms.ValidationError("Card number must contain only digits.")
        return number

    def clean_cvv(self):
        cvv = self.cleaned_data["cvv"]
        if not cvv.isdigit():
            raise forms.ValidationError("CVV must contain only digits.")
        return cvv

    def clean_expiry(self):
        expiry = self.cleaned_data["expiry"]
        try:
            month, year = expiry.split("/")
            month, year = int(month), 2000 + int(year)
        except ValueError:
            raise forms.ValidationError("Use the format MM/YY.")
        if not 1 <= month <= 12:
            raise forms.ValidationError("Month must be 01 to 12.")
        today = date.today()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError("This card has expired.")
        return expiry
