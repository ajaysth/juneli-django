from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control'
    }))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control'
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs[ 'placeholder']= 'First Name'
        self.fields['last_name'].widget.attrs[ 'placeholder']= 'Last Name'
        self.fields['phone_number'].widget.attrs[ 'placeholder']= 'Enter Phone number'
        self.fields['email'].widget.attrs[ 'placeholder']= 'Enter your email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        # Password validation rules
        if password:
            # Check minimum length
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long")
            
            # Check for uppercase letters
            if not any(char.isupper() for char in password):
                raise forms.ValidationError("Password must contain at least one uppercase letter")
            
            # Check for lowercase letters
            if not any(char.islower() for char in password):
                raise forms.ValidationError("Password must contain at least one lowercase letter")
            
            # Check for digits
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError("Password must contain at least one digit")
            
            # Check for special characters
            special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(char in special_characters for char in password):
                raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'      
            
            
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'