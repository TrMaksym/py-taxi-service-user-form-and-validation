from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from taxi.models import Driver, Car


class DriverCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Driver
        fields = UserCreationForm.Meta.fields + ('license_number',)


class DriverLicenseUpdateForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = ["license_number"]

    def clean_license_number(self):
        license_number = self.cleaned_data.get("license_number")
        if len(license_number) != 8:
            raise forms.ValidationError("Invalid license number")
        if not license_number[:3].isupper():
            raise forms.ValidationError("Invalid license number")
        if not license_number[:5].isdigit():
            raise forms.ValidationError("Invalid license number")

        return license_number

class DriverDeleteForm(forms.ModelForm):
    model = Driver
    fields = ["license_number"]
