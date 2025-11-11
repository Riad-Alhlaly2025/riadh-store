from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني'
        })
    )
    
    role = forms.ChoiceField(
        choices=UserProfile.USER_ROLES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label="الدور"
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add placeholders and classes to form fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'اختر اسم مستخدم'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'أنشئ كلمة مرور'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور'
        })
        
        # Update labels
        self.fields['username'].label = "اسم المستخدم"
        self.fields['email'].label = "البريد الإلكتروني"
        self.fields['password1'].label = "كلمة المرور"
        self.fields['password2'].label = "تأكيد كلمة المرور"
        self.fields['role'].label = "الدور"
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update the user's profile with the selected role
            user.userprofile.role = self.cleaned_data['role']
            user.userprofile.save()
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone_number']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'أدخل عنوان التوصيل الكامل'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            })
        }
        labels = {
            'shipping_address': 'عنوان التوصيل',
            'phone_number': 'رقم الهاتف'
        }