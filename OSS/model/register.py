from django import forms
from django.contrib.auth.forms import UserCreationForm
from GISDjango.models import User

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(required=True, label="Số điện thoại", max_length=15)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Địa chỉ giao hàng")

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'address')