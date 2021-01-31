from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Customer, Stock, Investment, Mails


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('cust_number', 'name', 'address', 'city', 'state', 'zipcode', 'email', 'cell_phone',)


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('customer', 'symbol', 'name', 'shares', 'purchase_price', 'purchase_date',)
        widgets = {
            'purchase_date': forms.DateInput(attrs={'class': 'datepicker', 'type': 'date', }),

        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ('customer', 'category', 'description', 'acquired_value', 'acquired_date', 'recent_value','recent_date')
        widgets = {
            'acquired_date': forms.DateInput(attrs={'class': 'datepicker', 'type': 'date', }),
            'recent_date': forms.DateInput(attrs={'class': 'datepicker', 'type': 'date', }),

        }


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email','first_name','last_name', 'password1', 'password2',)


class EmailForm(forms.ModelForm):
    email = forms.EmailField(max_length=200,
                             widget=forms.TextInput(attrs={'class': "form-control", 'id': "clientemail"}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))

    class Meta:
        model = Mails
        fields = ('email', 'subject', 'message', 'document',)
