from django import forms
from .models import AssignedTask, Report,CustomsPoint,Witness
from django.utils.translation import gettext_lazy as _

class AssignedTaskInlineForm(forms.ModelForm):
    class Meta:
        model = AssignedTask
        fields = ('workgroup', 'karar_date', 'salnan_jerime', 'trb','trb_date')

           # Explicitly set the widget to Decimal
    salnan_jerime = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
    )
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, you can customize help_text display here if needed
        self.fields['trb'].help_text = _('Töleg resminamasynyň (kwistansiýasynyň) belgisi')  # Explicitly setting help_text
        

class WitnessForm(forms.ModelForm):
    class Meta:
        model = Witness
        fields = ['fullname', 'address']  


    # Optional: Custom validation
    def clean_fullname(self):
        fullname = self.cleaned_data['fullname']
        if not fullname.strip():
            raise forms.ValidationError("Full name cannot be empty.")
        return fullname


      
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'  # Or specify the fields you need
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            "customsoffice": forms.Select(attrs={"class": "select2-dropdown"}),
            "customspoint": forms.Select(attrs={"class": "select2-dropdown"}),
            "customsofficer": forms.Select(attrs={"class": "select2-dropdown"}),
            "basisfordiscovery": forms.Select(attrs={"class": "select2-dropdown"}),
            "methodofdiscovery": forms.Select(attrs={"class": "select2-dropdown"}),
            "reasonforruleviolation": forms.Select(attrs={"class": "select2-dropdown"}),
            'administration_codexes': forms.SelectMultiple(attrs={
                'class': 'select2-dropdown',
                'data-placeholder': 'Saýlaň'
            }),
            "violation": forms.Select(attrs={"class": "select2-dropdown"}),
            "entry_exit_transit": forms.Select(attrs={"class": "select2-dropdown"}),
            "from_country": forms.Select(attrs={"class": "select2-dropdown"}),
            "to_country": forms.Select(attrs={"class": "select2-dropdown"}),
            "vehicle_brand": forms.Select(attrs={"class": "select2-dropdown"}),
            "transport_company": forms.Select(attrs={"class": "select2-dropdown"}),
        }
        exclude = ['created_at', 'updated_at']


class ReportAdminForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'
    
    # Override the field to be editable regardless of permissions
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['protocol_number'].disabled = False  # Ensure it's always editable
