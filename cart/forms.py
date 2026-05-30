from django import forms
from .models import Address, ReturnRequest


INDIAN_STATES = [
    ('', '-- Select State --'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Chandigarh', 'Chandigarh'),
    ('Puducherry', 'Puducherry'),
]


class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    address_type = forms.ChoiceField(
        choices=Address.ADDRESS_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = Address
        fields = [
            'full_name', 'phone', 'house_no', 'street',
            'area', 'city', 'state', 'pincode', 'landmark',
            'address_type', 'is_default',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10-digit mobile number', 'maxlength': '10'}),
            'house_no': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'House / Flat / Block No.'}),
            'street': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street, Road, Lane'}),
            'area': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Area / Colony / Locality'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'pincode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '6-digit PIN code', 'maxlength': '6'}),
            'landmark': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Near landmark (optional)'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = phone.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) != 10:
            raise forms.ValidationError('Enter a valid 10-digit mobile number.')
        return digits

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError('Enter a valid 6-digit PIN code.')
        return pincode


class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['request_type', 'reason', 'description']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-input'}),
            'reason': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Please describe the issue in detail...',
            }),
        }
