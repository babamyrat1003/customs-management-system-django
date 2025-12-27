from django.db import models
from django.utils.translation import gettext_lazy as _

from customs_registry.models import Country, ReasonForRuleViolation, Violation, CustomsOffice, CustomsPoint, Position, MethodOfDiscovery, MilitaryName, AdministrationCodex, BasisForDiscovery, CustomsOfficer
from django.core.validators import MinValueValidator
from django.apps import apps
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
import uuid
from datetime import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    related_users = models.ManyToManyField(User, related_name='related_users', verbose_name=_("Related Users"))

    class Meta:
        verbose_name = _("Ulanyjy rugsady")
        verbose_name_plural = _("Ulanyjy rugsatlar")

class Report(models.Model):

    ENTRY_EXIT_CHOICES = [
        ('giriş', _('Giriş')),
        ('çykyş', _('Çykyş')),
        ('üstaşyr', _('Üstaşyr')),
    ]

    ud_belgi = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default='',
        verbose_name=_('GKB-nyň ýüze çykarmagyna esas bolan resminama belgisi'),
        help_text=_('Customs kadalarynyň bozulmagynyň ýüze çykarmagyna esas bolan resminama belgisi(393 den 408-nji maddalar aralygy).'),
        db_index=True,
    )
    vehicle_brand = models.ForeignKey(
        "customs_registry.VehicleBrand",
        on_delete=models.PROTECT,
        related_name="reports",
        verbose_name
        =_('Vehicle Brand'),
        blank=True, 
        null=True, 
    )
    transport_company = models.ForeignKey(
        "customs_registry.TransportCompanyName",
        on_delete=models.PROTECT,
        related_name="reports",
        verbose_name=_('Transport Company Name'),
        blank=True, 
        null=True, 
    )
    ish_toplum_number = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_('Ish Toplum Number'),
        db_index=True
    )
    protocol_number = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Protocol Number')
    )
    report_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('Report date'),
        db_index=True
    )
    customsoffice = models.ForeignKey(
        CustomsOffice, 
        on_delete=models.CASCADE, 
        verbose_name=_('Customs Office'), 
        related_name='reports'
    )
    customspoint = models.ForeignKey(
        CustomsPoint, 
        on_delete=models.CASCADE, 
        verbose_name=_('Customs Point'), 
        related_name='reports'
    )

    customsofficer = models.ForeignKey(
        CustomsOfficer, 
        on_delete=models.CASCADE, 
        verbose_name=_('Customs Officer'), 
        related_name='reports'
    ) 
    basisfordiscovery = models.ForeignKey(
        BasisForDiscovery, 
        on_delete=models.CASCADE, 
        verbose_name=_('Basis for Discovery'), 

    )
    methodofdiscovery = models.ForeignKey(
        MethodOfDiscovery, 
        on_delete=models.CASCADE, 
        verbose_name=_('Method of Discovery'), 
        blank=True, 
        null=True, 
    )
    # reasonforruleviolation = models.ForeignKey(
    #     ReasonForRuleViolation, 
    #     on_delete=models.CASCADE, 
    #     verbose_name=_('Reason for Rule Violation'),
    #     blank=True, 
    #     null=True,  
    # )

    administration_codexes = models.ManyToManyField(
        AdministrationCodex,
        verbose_name=_('Administration Codexes'),
        related_name='some_other_models' 
    )       
    language_of_work_conducted = models.CharField(
        max_length=100,  
        default='Türkmen', 
        verbose_name=_('Language of Work Conducted')  
    )
    violation = models.ForeignKey(
        Violation, 
        on_delete=models.CASCADE, 
        verbose_name=_('Violation')
    ) 

    entry_exit_transit = models.CharField(
        max_length=20, 
        choices=ENTRY_EXIT_CHOICES, 
        verbose_name=_('Entry/Exit/Transit'),
        db_index=True
    )
    from_country = models.ForeignKey(
        'customs_registry.Country',  
        related_name='from_country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('From Country')
    )
    to_country = models.ForeignKey(
        'customs_registry.Country',  
        related_name='to_country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('To Country')
    )
    carnumber = models.CharField(
        max_length=20,  
        verbose_name=_('Car Number'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Created by User'),
        related_name='reports',
    )
    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['ud_belgi'], 
                name='unique_ud_belgi_combination',
                condition=models.Q(ud_belgi__isnull=False, ud_belgi__gt='')  # Only apply when both are non-empty
            )
        ]
        

    def __str__(self):
        # Concatenate relevant fields to create a meaningful representation
        return f"{self.protocol_number or 'No Protocol'} - {self.customsofficer.name} {self.customsofficer.midname} {self.customsofficer.surname}".strip()
    


class Witness(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='witnesses',
        verbose_name=_("Report"),
    )
    fullname = models.CharField(max_length=255, verbose_name=_("Full Name"), blank=True, null=True, )
    address = models.CharField(max_length=512, verbose_name=_("Witness Address"),blank=True, null=True,)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _("Witness")
        verbose_name_plural = _("Witnesses")

    def __str__(self):
        return self.fullname
    
def rename_pdf(instance, filename):
    """Generate a unique filename for uploaded PDFs and place it inside the correct directory format."""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"  # Generate a unique filename
    today = datetime.today()
    return os.path.join(f"nusgalar/{today.year}/{today.month}/", new_filename)  # Correct directory format

class AssignedTask(models.Model):
    karar_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('Karar date')
    )
    trb = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default='',
        verbose_name=_('TRB'),
        help_text=_('Töleg resminamasynyň (kwistansiýasynyň) belgisi')
    )

    trb_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('TRB senesi'),
        help_text=_('Töleg resminamasynyň belgisiniň senesi')
    )
    salnan_jerime = models.DecimalField(
        max_digits=12,  
        decimal_places=2, 
        verbose_name=_('Salnan jerime'),
        help_text=_('Total Payment in Manat'),
        validators=[
            MinValueValidator(0)
        ],
        blank=True, 
        null=True,
    )
    tolenen_manat = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Tölenen jerime (Manat)'),
        help_text=_('Tölenen jerime (Manat)'),
        validators=[
            MinValueValidator(0)  # Ensure manat is non-negative
        ],
        blank=True, 
        null=True,
    )
    workgroup = models.ForeignKey(
        'customs_registry.Workgroup',
        on_delete=models.CASCADE,
        verbose_name=_('Workgroup'),
        related_name='assigned_tasks'  # Related name for reverse relationship
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('The date and time when this record was created.'),
        db_index=True  # Add an index if filtering by date
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_('The date and time when this record was last updated.'),
        db_index=True  # Add an index if filtering by date
    )
    report = models.ForeignKey(
        'report.Report',
        on_delete=models.CASCADE,
        related_name='assigned_tasks',  # Related name for reverse relationship
        verbose_name=_('Report')
    ) 

    bilermen_nusga = models.FileField(
        upload_to= rename_pdf,
        validators=[FileExtensionValidator(['pdf'])],  # Restrict to PDF files
        blank=True,
        null=True,
        verbose_name=_('Bilermen nusga (PDF)'),
        help_text=_(' Bilermen nusgasyny ýükläň.')
    )
    class Meta:
        verbose_name = _('Assigned Task')
        verbose_name_plural = _('Assigned Tasks')
        ordering = ['-created_at']  # Default ordering by created_at in descending order
        constraints = [
            models.UniqueConstraint(
                fields=['trb'], 
                name='unique_trb_combination',
                condition=models.Q(trb__isnull=False, trb__gt='')  # Only apply when both are non-empty
            )
        ]


    def __str__(self):
        return f"{self.workgroup} - {self.salnan_jerime} Manat"
    
class AssignedLetter(models.Model):
    # Foreign key to LettersForAction model
    letterforaction = models.ForeignKey(
        'customs_registry.LettersForAction',
        on_delete=models.CASCADE,
        verbose_name=_('Letter for Action'),
        related_name='assigned_letters'  # Adjusted to plural form for clarity
    )

    # Number field with a regex validator for specific format (if applicable)
    number = models.CharField(
        max_length=50,
        verbose_name=_("Letter Number"),
        help_text=_('The unique number identifying this letter.')
        
    )

    # Date field with verbose name and help text
    date = models.DateField(
        verbose_name=_('Letter Date'),
        help_text=_('The date when the letter was issued.')
    )

    # Foreign key to AssignedTask model
    assignedtask = models.ForeignKey(
        'AssignedTask',
        on_delete=models.CASCADE,
        verbose_name=_('Assigned Task'),
        related_name='assigned_letters'
    )

    # Auto-created and updated timestamps with indexing for performance optimization
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('The date and time when this record was created.'),
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_('The date and time when this record was last updated.'),
        db_index=True
    )

    care_nusga = models.FileField(
        upload_to= rename_pdf,
        validators=[FileExtensionValidator(['pdf'])],  # Restrict to PDF files
        blank=True,
        null=True,
        verbose_name=_('Çäre nusga (PDF)'),
        help_text=_(' Çäre görmek üçin hatyň nusgasyny ýükläň.')
    )

    class Meta:
        verbose_name = _('Assigned Letter')
        verbose_name_plural = _('Assigned Letters')
        ordering = ['-date']  # Default ordering by date in descending order

    def __str__(self):
        return f"Letter {self.number} for {self.assignedtask} on {self.date}"
