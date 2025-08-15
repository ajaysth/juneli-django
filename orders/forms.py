from django import forms
from .models import Order
import re

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = {'first_name','last_name','phone','email','address_line_1','address_line_2','country', 'state','city','order_note'}
        
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field != 'order_note':
                self.fields[field].widget.attrs['required'] = 'required'
    
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long")
        if not first_name.isalpha():
            raise forms.ValidationError("First name must contain only letters")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long")
        if not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only letters")
        return last_name
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Remove common separators
        phone_digits = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        if not phone_digits.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise forms.ValidationError("Phone number must be between 10-15 digits")
        
        return phone
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address")
        return email
    
    def clean_address_line_1(self):
        address = self.cleaned_data['address_line_1']
        if len(address) < 5:
            raise forms.ValidationError("Address must be at least 5 characters long")
        return address
    
    def clean_city(self):
        city = self.cleaned_data['city']
        if len(city) < 2:
            raise forms.ValidationError("City must be at least 2 characters long")
        if not city.replace(' ', '').isalpha():
            raise forms.ValidationError("City must contain only letters and spaces")
        return city
    
    def clean_state(self):
        state = self.cleaned_data['state']
        if len(state) < 2:
            raise forms.ValidationError("State must be at least 2 characters long")
        if not state.replace(' ', '').isalpha():
            raise forms.ValidationError("State must contain only letters and spaces")
        return state
    
    def clean_country(self):
        country = self.cleaned_data['country']
        if len(country) < 2:
            raise forms.ValidationError("Country must be at least 2 characters long")
        if not country.replace(' ', '').isalpha():
            raise forms.ValidationError("Country must contain only letters and spaces")
        return country
        
        