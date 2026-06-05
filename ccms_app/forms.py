from django import forms

from .models import Branch, Package, Vehicle


INPUT_CLASS = 'form-input'
SELECT_CLASS = 'form-input'
TEXTAREA_CLASS = 'form-input min-h-[80px]'


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'code', 'location', 'contact_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Branch name'}),
            'code': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. NBO-01'}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'City, address'}),
            'contact_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+254...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'vehicle_type', 'driver_name', 'driver_phone', 'status']
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. KCA 123A'}),
            'vehicle_type': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Van, Truck, ...'}),
            'driver_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'driver_phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+254...'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
        }


class PackageRegistrationForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = [
            'sender_full_name', 'sender_id_number', 'sender_phone',
            'receiver_full_name', 'receiver_id_number', 'receiver_phone',
            'package_type', 'description', 'quantity', 'weight',
            'origin_branch', 'destination_branch', 'assigned_vehicle', 'transport_fee',
        ]
        widgets = {
            'sender_full_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'sender_id_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'National ID / Passport'}),
            'sender_phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+254...'}),
            'receiver_full_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'receiver_id_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'National ID / Passport'}),
            'receiver_phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+254...'}),
            'package_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1}),
            'weight': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 0, 'step': '0.01'}),
            'origin_branch': forms.Select(attrs={'class': SELECT_CLASS}),
            'destination_branch': forms.Select(attrs={'class': SELECT_CLASS}),
            'assigned_vehicle': forms.Select(attrs={'class': SELECT_CLASS}),
            'transport_fee': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        active_branches = Branch.objects.filter(is_active=True)
        self.fields['origin_branch'].queryset = active_branches
        self.fields['destination_branch'].queryset = active_branches
        self.fields['assigned_vehicle'].queryset = Vehicle.objects.exclude(
            status='inactive',
        ).order_by('plate_number')
        self.fields['assigned_vehicle'].required = False
        self.fields['assigned_vehicle'].empty_label = '— Assign later —'

        if user and user.is_branch_officer and user.branch_id:
            self.fields['origin_branch'].initial = user.branch
            self.fields['origin_branch'].disabled = True

    def clean(self):
        cleaned = super().clean()
        origin = cleaned.get('origin_branch')
        destination = cleaned.get('destination_branch')

        if self.user and self.user.is_branch_officer and self.user.branch_id:
            cleaned['origin_branch'] = self.user.branch

        if origin and destination and origin == destination:
            self.add_error('destination_branch', 'Destination must differ from origin branch.')

        return cleaned
