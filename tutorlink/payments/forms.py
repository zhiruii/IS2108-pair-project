from django import forms


class PaymentForm(forms.Form):
    name_on_card = forms.CharField(max_length=100)
    card_number = forms.CharField(
        min_length=12,
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "1234567812345678"}),
    )
    expiry = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={"placeholder": "MM/YY"}),
    )
    
    cvv = forms.CharField(
        min_length=3, 
        max_length=3,
        label="CVV",
        widget=forms.TextInput(attrs={"placeholder": "123"}),
    )

    def clean_card_number(self):
        number = self.cleaned_data["card_number"]
        if not number.isdigit():
            raise forms.ValidationError("Card number must contain only digits.")
        return number
