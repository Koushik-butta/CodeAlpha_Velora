from django import forms
from django.core.exceptions import ValidationError

from shop.models import Product, Category, Review


class MultipleFileInput(forms.Widget):
    """Custom widget for multiple file uploads."""
    input_type = 'file'
    needs_multipart_form = True

    def __init__(self, attrs=None):
        default_attrs = {'multiple': True, 'accept': 'image/*', 'class': 'form-input', 'id': 'id_images'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        return None  # Don't show a value

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

    def render(self, name, value, attrs=None, renderer=None):
        from django.forms.utils import flatatt
        from django.utils.safestring import mark_safe
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs['type'] = 'file'
        final_attrs['name'] = name
        return mark_safe(f'<input{flatatt(final_attrs)}>')


class MultipleFileField(forms.Field):
    """Field that handles multiple file uploads."""
    widget = MultipleFileInput

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def clean(self, data):
        if not data:
            return []
        # data is a list of InMemoryUploadedFile objects
        return [f for f in data if f]


class ProductForm(forms.ModelForm):
    """Form for creating and editing product listings."""

    images = MultipleFileField(
        help_text='Upload up to 5 images. First image becomes the primary.',
    )

    class Meta:
        model = Product
        fields = (
            'title',
            'category',
            'listing_type',
            'brand',
            'model_name',
            'condition',
            'price',
            'original_price',
            'description',
            'city',
            'state',
            'exchange_available',
            'exchange_for',
            'return_policy',
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'formInput',
                'placeholder': 'e.g. iPhone 13 Pro Max 256GB Space Grey',
            }),
            'category': forms.Select(attrs={'class': 'formInput'}),
            'listing_type': forms.Select(attrs={'class': 'formInput'}),
            'brand': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'e.g. Apple'}),
            'model_name': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'e.g. iPhone 13 Pro Max'}),
            'condition': forms.Select(attrs={'class': 'formInput'}),
            'price': forms.NumberInput(attrs={'class': 'formInput', 'placeholder': '0.00', 'step': '0.01'}),
            'original_price': forms.NumberInput(attrs={
                'class': 'formInput',
                'placeholder': 'Original / MRP (optional)',
                'step': '0.01',
            }),
            'description': forms.Textarea(attrs={
                'class': 'formInput',
                'rows': 5,
                'placeholder': 'Describe your product, its condition, any accessories included…',
            }),
            'city': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'formInput', 'placeholder': 'State'}),
            'exchange_available': forms.CheckboxInput(attrs={'class': 'formCheckbox'}),
            'exchange_for': forms.Textarea(attrs={
                'class': 'formInput',
                'rows': 3,
                'placeholder': 'What would you like in exchange? (optional)',
            }),
            'return_policy': forms.Select(attrs={'class': 'formInput'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Price cannot be negative.')
        return price

    def clean_original_price(self):
        original_price = self.cleaned_data.get('original_price')
        if original_price is not None and original_price < 0:
            raise ValidationError('Original price cannot be negative.')
        return original_price


class ReviewForm(forms.ModelForm):
    """Form for submitting a product review."""

    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'ratingRadio'}),
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'formInput',
            'rows': 4,
            'placeholder': 'Share your experience with this product or seller…',
        }),
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            raise ValidationError('Please select a valid rating.')
        if rating not in range(1, 6):
            raise ValidationError('Rating must be between 1 and 5.')
        return rating
