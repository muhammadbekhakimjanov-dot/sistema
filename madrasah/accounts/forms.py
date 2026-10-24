from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "last_name", "first_name", "middle_name",
                  "phone", "email", "role"]


class DeactivateForm(forms.Form):
    reason = forms.CharField(label="Себеби", max_length=255)
