from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Lower
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
import os
import uuid
from datetime import datetime

class CustomsOffice(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Customs Office Name'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    code = models.CharField(max_length=5, null=True, blank=True, default=None, unique=True, verbose_name=_('Customs Office Code'))
   
    class Meta:
        verbose_name = _('Customs Office')
        verbose_name_plural = _('Customs Offices')
        ordering = ['name']  # Orders by name by default
        indexes = [
            models.Index(fields=['name'], name='customs_office_name_idx'),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'


    def delete(self, *args, **kwargs):
        """Custom behavior for delete can go here if needed, such as soft deletion."""
        super().delete(*args, **kwargs)

class CustomsPoint(models.Model):
    customsoffice = models.ForeignKey(CustomsOffice, on_delete=models.CASCADE, verbose_name=_('Customs Office'), related_name='customs_points')
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    code = models.CharField(max_length=5, null=True, blank=True, default=None, unique=True, verbose_name=_('Customs Point Code'))

    class Meta:
        verbose_name = _('Customs Point')
        verbose_name_plural = _('Customs Points')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['customsoffice', 'name'], name='unique_customsoffice_name')
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'


    def clean(self):
        super().clean()
        if CustomsPoint.objects.filter(customsoffice=self.customsoffice, name=self.name).exclude(id=self.id).exists():
            raise ValidationError(_('A Customs Point with this name already exists in this office.'))

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Country Name'))
    code = models.CharField(max_length=3, unique=True, verbose_name=_('Country Code'))  # ISO 3166-1 alpha-3 code
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.code.upper()} - {self.name}"
    

class City(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('City Name'))
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='cities', verbose_name=_('Country'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Product Name'))
    productcategory = models.ForeignKey('ProductCategory',
                                        on_delete=models.CASCADE, 
                                        related_name='products',    
                                        verbose_name=_('Product Category'),
                                        blank=True,
                                        null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_product_name_insensitive'
            )
        ]

    def __str__(self):
        return self.name.capitalize()

    def save(self, *args, **kwargs):
        # Capitalize only the first letter, leave the rest of the name unchanged
        self.name = self.name[:1].upper() + self.name[1:]
        super().save(*args, **kwargs)

class UnitOfMeasurement(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Unit of Measurement'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Unit of Measurement')
        verbose_name_plural = _('Units of Measurement')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class MethodOfDiscovery(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Method of Discovery'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Method of Discovery')
        verbose_name_plural = _('Methods of Discovery')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name
    
class ReasonForRuleViolation(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Reason for Rule Violation'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Reason for Rule Violation')
        verbose_name_plural = _('Reasons for Rule Violation')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class BasisForDiscovery(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Basis for Discovery'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Basis for Discovery')
        verbose_name_plural = _('Basiss for Discovery')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class Workgroup(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Workgroup'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Workgroup')
        verbose_name_plural = _('Workgroups')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class LettersForAction(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Letters for Action'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Letters for Action')
        verbose_name_plural = _('Letters for Action')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class MilitaryName(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_('Military Name'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Military Name')
        verbose_name_plural = _('Military Names')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_('Position'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name
    
class AdministrationCodex(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('Administration Codex'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('AdministrationCodex')
        verbose_name_plural = _('AdministrationCodexes')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name
    
class CustomsOfficer(models.Model):
    name = models.CharField(
        max_length=255, 
        verbose_name=_('Name'), 
        blank=False,  # Required field (if applicable)
    )
    surname = models.CharField(
        max_length=255, 
        verbose_name=_('Surname'), 
        blank=False,  # Required field (if applicable)
    )
    midname = models.CharField(
        max_length=255, 
        verbose_name=_('Middle Name'), 
        null=True, 
        blank=True,  # Optional field for forms
        default='',   # Avoid using an empty string default unless necessary
    )
    position = models.ForeignKey(
        'Position', 
        on_delete=models.CASCADE, 
        verbose_name=_('Position')
    )
    militaryname = models.ForeignKey(
        'MilitaryName', 
        on_delete=models.CASCADE, 
        verbose_name=_('Military Name')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Customs Officer')
        verbose_name_plural = _('Customs Officers')
        ordering = ['surname', 'name']  # Order by surname and then by name
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'surname', 'militaryname'], 
                name='unique_customs_officer'
            )
        ]

    def __str__(self):
        """Return a readable string representation of the customs officer, including military name and position."""
        militaryname = self.militaryname if self.militaryname else ''
        surname = self.surname if self.surname else ''
        name = self.name if self.name else ''
        midname = self.midname if self.midname else ''
        position = self.position if self.position else ''

        # Combine the fields with spaces, stripping any extra whitespace
        return f"{militaryname} {surname} {name} {midname} ({position})".strip()

    def get_full_name(self):
        """Return the full name of the customs officer, including military name and position."""
        return f"{self.militaryname} {self.surname} {self.name} {self.midname} ({self.position})".strip()
        
class Violation(models.Model):
    TYPE_CHOICES = [
        ('legal entity', _('legal entity')),
        ('individual', _('individual')),
        ('official', _('official')),
    ]

    # Common fields for all types
    violation_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        verbose_name=_('Violation Type')
    )

    # Fields for legal entity
    company_name = models.CharField(
        unique=True,
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Company Name'),
        help_text=_('Name of the company involved in the violation. Only applicable for legal entity.')

    )
    company_boss_fullname = models.CharField(
        unique=True,
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Company Boss Fullname'),
    )
    address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Address')
    )
    phone = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Phone'),
        help_text=_('Format: +99369999999 or 99369999999')
    )

    # Fields for individual and official
    violator_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Violator Name')
    )
    violator_surname = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Violator Surname')
    )
    father_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Father Name')
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('Date of Birth')
    )
    place_of_birth = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Place of Birth')
    )
    passport_number = models.CharField(
        unique=True,
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Passport Number')
    )
    passport_issue_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('Passport Issue Date')
    )
    nationality = models.ForeignKey(
        'Country', 
        related_name='nationality_country', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Nationality')
    )
    violator_address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Violator Address')
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Created At'),
        null=True,  # Allow null values temporarily for migration
        blank=True  # Allow blank values temporarily for migration
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Updated At'),
        null=True,  # Allow null values temporarily for migration
        blank=True  # Allow blank values temporarily for migration
    )

    

    @property
    def full_name(self):
        """
        Returns the combined full name for the violator.
        Includes name, surname, and father name.
        """
        parts = [self.violator_name, self.violator_surname, self.father_name]
        return " ".join([part for part in parts if part])  # Join non-empty parts
    

    def __str__(self):
        # For 'legal entity', return the company name if present
        if self.violation_type == 'legal entity' and self.company_name:
            return f"{self.get_violation_type_display()}: {self.company_name}"
        
        # For 'individual' or 'official', return the full name
        elif self.violation_type in ['individual', 'official']:
            # Combine violator_name, violator_surname, and father_name into full_name
            full_name = " ".join(filter(None, [self.violator_surname, self.violator_name,  self.father_name]))
            
            # Return full_name if not empty, otherwise just return the violation type
            return f"{self.get_violation_type_display()}: {full_name}" if full_name else f"{self.get_violation_type_display()}"
        
        # Fallback to violation type only if none of the above is applicable
        return self.get_violation_type_display()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'company_name', 
                    'violator_name', 
                    'violator_surname', 
                    'father_name', 
                    'date_of_birth'
                ],
                name='unique_violation_constraint'
            ),
        ]
        verbose_name = _('Violation')
        verbose_name_plural = _('Violations')

class StoredGood(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name=_('Product'),
        help_text=_('Select the product being stored.'),
        blank=False,
        null=False 
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Amount'),
        validators=[MinValueValidator(1)],  # Ensures the amount is positive
        help_text=_('The quantity of the product stored.'),
        blank=False,
        null=False 
    )
    unitofmeasurement = models.ForeignKey(
        'UnitOfMeasurement',
        on_delete=models.CASCADE,
        verbose_name=_('Unit of Measurement'),
        help_text=_('The unit of measurement for the stored amount (e.g., kg, liters).'),
        blank=False,
        null=False 
    )
    note = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('StoredGood Note'),
        help_text=_('Additional notes or comments about this stored good. Optional.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('The date and time when this record was created.')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_('The date and time when this record was last updated.')
    )

    report = models.ForeignKey('report.Report', on_delete=models.CASCADE, related_name='stored_goods')
    
    reasonforruleviolation = models.ForeignKey(
        ReasonForRuleViolation, 
        on_delete=models.CASCADE, 
        verbose_name=_('Reason for Rule Violation'),
        blank=True, 
        null=True,  
    )
    class Meta:
        verbose_name = _('Stored Good')
        verbose_name_plural = _('Stored Goods')
        ordering = ['-created_at']  # Sort by creation date, most recent first
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['product', 'unitofmeasurement'], 
        #         name='unique_product_unit'
        #     )  # Ensure unique product-unit combination
        # ]

    def __str__(self):
        return f"{self.product} - {self.amount} {self.unitofmeasurement}"

    def clean(self):
        """
        Custom validation for the StoredGood model.
        This can be used to ensure additional logic (e.g., preventing negative amounts) 
        before saving to the database.
        """
        super().clean()
        if self.amount <= 0:
            raise ValidationError(_('Amount must be greater than zero.'))
        
from django.utils.html import format_html

class StoredGoodImage(models.Model):
    stored_good = models.ForeignKey(
        StoredGood, 
        related_name='images', 
        on_delete=models.CASCADE, 
        verbose_name=_('Stored Good'),
  
    )
    image = models.ImageField(upload_to='stored_good_images/', verbose_name=_('Image'))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))

    def __str__(self):
        return f"Image for {self.stored_good} - {self.description or 'No description'}"

    def image_tag(self):
        return format_html('<img src="{}" style="width: 100px; height: auto;" />', self.image.url)
    
    image_tag.short_description = 'Image'

    class Meta:
        verbose_name = _('Stored Good Image')
        verbose_name_plural = _('Stored Good Images')


class VehicleBrand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Vehicle Brand'))
    # vehicle_types = models.ManyToManyField(VehicleType, related_name="brands", verbose_name=_('Vehicle Types'))
    
    class Meta:
        verbose_name = _('Vehicle Brand')
        verbose_name_plural = _('Vehicle Brands')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class TransportCompanyName(models.Model):
    name = models.CharField(max_length=255,unique=True,verbose_name=_('Transport Company Name'))
    
    # Optional: verbose name for more readable model representation
    class Meta:
        verbose_name = _('Transport Company Name')
        verbose_name_plural = _('Transport Company Names')
        
    def __str__(self):
        return self.name
    

class ProductCategory(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_('Product Category'))
    
    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DernewGornush(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_('Derňewiň görnüşi'))
    
    class Meta:
        verbose_name = _('Derňewiň görnüşi')
        verbose_name_plural = _('Derňewiň görnüşleri')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class TJK(models.Model):
    name = models.CharField(max_length=450, unique=True, verbose_name=_('TJK-ne esas bolan madda'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('TJK-ne esas bolan madda')
        verbose_name_plural = _('TJK-ne esas bolan maddalar')
        ordering = ['name']  # Optional, orders by 'name'

    def __str__(self):
        return self.name
    
def rename_pdf(instance, filename):
    """Generate a unique filename for uploaded PDFs and place it inside the correct directory format."""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"  # Generate a unique filename
    today = datetime.today()
    return os.path.join(f"nusgalar/{today.year}/{today.month}/", new_filename)  # Correct directory format

class DernewNetijesi(models.Model):
    dernew = models.ForeignKey(
        'DernewGornush',
        on_delete=models.SET_NULL,  # Avoids accidental deletion
        verbose_name=_('Derňewiň netijesi'),
        help_text=_('Derňewiň netijesini saýlaň'),
        blank=True,
        null=True,
        related_name='netijeler',  # Improves query readability
        db_index=True  # Optimized queries
    )
    tjk = models.ForeignKey(
        'TJK',
        on_delete=models.SET_NULL,
        verbose_name=_('TJK-ne esas bolan madda'),
        help_text=_('TJK-ne esas bolan maddany saýlaň'),
        blank=True,
        null=True,
        related_name='esas_bolan_maddalar',
        db_index=True
    )
    workgroup = models.ForeignKey(
        'Workgroup',
        on_delete=models.SET_NULL,
        verbose_name=_('Workgroup'),
        help_text=_('Görlen çäräni saýlaň'),
        blank=True,
        null=True,
        related_name='dernew_workgroups',
        db_index=True
    )
    gorlen_care = models.TextField(
        blank=True, 
        verbose_name=_('Görlen çäre'),
        help_text=_('Görlen çäre barada giňişleýin maglumat')
    )

        # PDF Upload Field
    hatyn_nusgasy = models.FileField(
        upload_to=rename_pdf,
        validators=[FileExtensionValidator(['pdf'])],  # Restrict to PDFs only
        blank=True,
        null=True,
        verbose_name=_('Hatyň nusgasy (PDF)'),
        help_text=_('PDF görnüşinde derňew hasabatyny ýükläň')
    )

    assignedtask = models.ForeignKey(
        'report.AssignedTask',
        on_delete=models.CASCADE,
        verbose_name=_('Assigned Task'),
        related_name='dernewin_netijesi',
        blank=True,
        null=True,
        db_index=True
    )
    class Meta:
        verbose_name = _('Derňew netijesi')
        verbose_name_plural = _('Derňew netijeleri')
        ordering = ['dernew']

    def __str__(self):
        return f"{self.dernew} - {self.tjk} - {self.workgroup}"

