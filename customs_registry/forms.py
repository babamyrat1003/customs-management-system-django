from django import forms
from report.models import Report
from .models import Country, CustomsPoint, MethodOfDiscovery, Product, StoredGood, Violation
from django.forms import inlineformset_factory


class CustomsPointForm(forms.ModelForm):
    class Meta:
        model = CustomsPoint
        fields = ['customsoffice', 'name','code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','style': 'width: 500px;'}),            
        }

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name').capitalize()
        if Product.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(_('A product with this name already exists.'))
        return name

class MethodOfDiscoveryForm(forms.ModelForm):
    class Meta:
        model = MethodOfDiscovery
        fields = ['name', 'description']

    # Override the widget for the 'name' field to add custom CSS
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'style': 'width: 100%;'})  # Set width to 100%

class ReasonForRuleViolationForm(forms.ModelForm):
    class Meta:
        model = MethodOfDiscovery
        fields = ['name', 'description']

    # Override the widget for the 'name' field to add custom CSS
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'style': 'width: 100%;'})  # Set width to 100%

class ViolationAdminForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        violation_type = self.instance.violation_type if self.instance else None
        self.set_required_fields(violation_type)

    def set_required_fields(self, violation_type):
        """Set the required fields based on the violation type."""
        # Clear all required fields first
        for field in self.fields.values():
            field.required = False

        # Set required fields for each type
        if violation_type == 'legal entity':
            self.fields['company_name'].required = True
            self.fields['address'].required = True
        elif violation_type == 'individual' or violation_type == 'official':
            self.fields['violator_name'].required = True
            self.fields['violator_surname'].required = True
            self.fields['date_of_birth'].required = True
            self.fields['place_of_birth'].required = True
            self.fields['violator_address'].required = True

    def clean(self):
        """Validate the form and raise errors for missing required fields."""
        cleaned_data = super().clean()
        violation_type = cleaned_data.get('violation_type')

        # Check required fields based on violation type
        if violation_type == 'legal entity':
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'This field is required for legal entity.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'This field is required for legal entity.')
        elif violation_type in ['individual', 'official']:
            if not cleaned_data.get('violator_name'):
                self.add_error('violator_name', 'This field is required for individual/official.')
            if not cleaned_data.get('violator_surname'):
                self.add_error('violator_surname', 'This field is required for individual/official.')
            if not cleaned_data.get('date_of_birth'):
                self.add_error('date_of_birth', 'This field is required for individual/official.')
            if not cleaned_data.get('place_of_birth'):
                self.add_error('place_of_birth', 'This field is required for individual/official.')
            if not cleaned_data.get('violator_address'):
                self.add_error('violator_address', 'This field is required for individual/official.')

        return cleaned_data
    
