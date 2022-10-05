from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class ShippingAddressForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'floatingInput',
        'placeholder': 'Street and house number'
    }))
    apartment = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'floatingApartment',
        'placeholder': 'Apartment'
    }))
    country = CountryField(blank_label='Select country').formfield(widget=CountrySelectWidget(attrs={
        'class': 'form-control',
        'id': 'floatingSelect',
        'placeholder': 'Select country',
        'aria-label': 'Select country'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'floatingZip',
        'placeholder': 'Zip'
    }))
