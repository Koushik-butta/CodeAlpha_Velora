from django import forms
from django.core.exceptions import ValidationError

from swap.models import ExchangeRequest
from shop.models import Product


class ExchangeRequestForm(forms.ModelForm):
    """Form for initiating a product exchange request."""

    offered_product = forms.ModelChoiceField(
        queryset=Product.objects.none(),  # Will be set in __init__
        empty_label='— Select one of your products to offer —',
        widget=forms.Select(attrs={'class': 'formInput'}),
        help_text='Choose a product from your active listings to offer in exchange.',
    )
    cash_adjustment = forms.DecimalField(
        required=False,
        initial=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'formInput',
            'placeholder': '0.00 (positive = you pay extra, negative = you receive)',
            'step': '0.01',
        }),
        help_text='Optional cash top-up. Positive if you pay extra; negative if you receive cash.',
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'formInput',
            'rows': 4,
            'placeholder': 'Write a message to the seller — explain why this exchange works for both…',
        }),
    )

    class Meta:
        model = ExchangeRequest
        fields = ('offered_product', 'cash_adjustment', 'message')

    def __init__(self, requester, *args, **kwargs):
        """Filter offered_product to the requester's own active, unsold products."""
        super().__init__(*args, **kwargs)
        self.fields['offered_product'].queryset = Product.objects.filter(
            seller=requester,
            is_active=True,
            is_sold=False,
        ).order_by('-created_at')

    def clean_cash_adjustment(self):
        value = self.cleaned_data.get('cash_adjustment')
        if value is None:
            return 0
        return value
