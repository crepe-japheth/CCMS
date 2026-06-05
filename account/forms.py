from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from ccms_app.models import Branch

from .models import User, UserRole, UserStatus


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Username',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Password',
        }),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.status == UserStatus.INACTIVE:
            raise forms.ValidationError(
                'This account has been deactivated. Contact your administrator.',
                code='inactive',
            )


class UserCreateForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-input'}))
    role = forms.ChoiceField(choices=UserRole.choices, widget=forms.Select(attrs={'class': 'form-input'}))
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        empty_label='— No branch —',
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = [
            'username', 'full_name', 'email', 'phone_number',
            'role', 'branch', 'password1', 'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-input'
        self.fields['password2'].widget.attrs['class'] = 'form-input'

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        branch = cleaned.get('branch')
        if role == UserRole.BRANCH_OFFICER and not branch:
            self.add_error('branch', 'Branch officers must be assigned to a branch.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data.get('email', '')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.role = self.cleaned_data['role']
        user.branch = self.cleaned_data.get('branch')
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep current'}),
        label='New password',
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'role', 'branch', 'status']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
            'branch': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True)
        self.fields['branch'].required = False
        self.fields['branch'].empty_label = '— No branch —'

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        branch = cleaned.get('branch')
        if role == UserRole.BRANCH_OFFICER and not branch:
            self.add_error('branch', 'Branch officers must be assigned to a branch.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('new_password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
