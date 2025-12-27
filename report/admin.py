from django import forms
from django.contrib import admin
import nested_admin
from admin_searchable_dropdown.filters import AutocompleteFilter
from customs_registry.admin import DernewNetijesiInline, StoredGoodInline
from .models import AssignedLetter, AssignedTask, Report
from customs_registry.models import CustomsOffice, CustomsPoint,AdministrationCodex
from django.utils.translation import gettext_lazy as _
from .models import Witness
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
import openpyxl
from django.http import HttpResponse
from django.utils.timezone import now

from datetime import datetime
from .forms import AssignedTaskInlineForm, ReportAdminForm 
from django.utils.translation import pgettext_lazy
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.contrib.auth.models import User

from .utils import export_report_to_excel, export_grouped_report
from django.utils.html import format_html

from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'related_users_list')  # Display the user and related users in the list view
    search_fields = ('user__username',)  # Allows searching by username
    filter_horizontal = ('related_users',)  # Adds a horizontal filter for ManyToMany field

    # Custom method to display related users in a more readable format
    def related_users_list(self, obj):
        return ", ".join([user.username for user in obj.related_users.all()])
    related_users_list.short_description = 'Related Users'  # Set the column name

admin.site.register(UserProfile, UserProfileAdmin)

class WitnessInline(nested_admin.NestedTabularInline): 
    model = Witness
    fields = ('fullname', 'address')  
    extra = 1  
    verbose_name = _("Witness")
    verbose_name_plural = _("Witnesses")
    show_change_link = True   
    

    def get_extra(self, request, obj=None, **kwargs):       
        if obj:
            return 0 
        return 1 

class AssignedLetterInline(nested_admin.NestedTabularInline): 
    model = AssignedLetter
    fields = ('letterforaction','number', 'date', 'assignedtask','care_nusga','hatyn_nusgasy_link')
    extra = 1  
    verbose_name = _("Assigned Letter")
    verbose_name_plural = _("Assigned Letters")
    readonly_fields = ('hatyn_nusgasy_link',)

    def hatyn_nusgasy_link(self, obj):
        """Show a link to download the uploaded PDF file."""
        if obj.care_nusga:
            return format_html('<a href="{}" target="_blank">📄 Download PDF</a>', obj.care_nusga.url)
        return "No file uploaded"
    
    hatyn_nusgasy_link.short_description = "Çäre nusgasy PDF"
    
  

    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0  
        return 1  

class AssignedTaskInline(nested_admin.NestedStackedInline): 
    model = AssignedTask
    fields = ('workgroup','karar_date', 'salnan_jerime', 'tolenen_manat','trb','trb_date','bilermen_nusga','hatyn_nusgasy_link')
    extra = 1  
    verbose_name = _("Assigned Task")
    verbose_name_plural = _("Assigned Tasks")
    inlines = [AssignedLetterInline, DernewNetijesiInline]   
    form = AssignedTaskInlineForm
    show_change_link = True   
    readonly_fields = ('hatyn_nusgasy_link',)

    def hatyn_nusgasy_link(self, obj):
        """Show a link to download the uploaded PDF file."""
        if obj.bilermen_nusga:
            return format_html('<a href="{}" target="_blank">📄 Download PDF</a>', obj.bilermen_nusga.url)
        return "No file uploaded"
    
    hatyn_nusgasy_link.short_description = "Bilermen nusgasy PDF"
    
  
    def get_extra(self, request, obj=None, **kwargs):       
        if obj:
            return 0 
        return 1 
    
class OriginCountryFilter(AutocompleteFilter):
    title = _('Haýsy ýurtdan?') 
    field_name = 'from_country' 

class DestinationCountryFilter(AutocompleteFilter):
    title = _('Haýsy ýurtda?') 
    field_name = 'to_country' 

class CustomsOfficeFilter(AutocompleteFilter):
    title = _('Customs Office')
    field_name = 'customsoffice'

class CustomsPointFilter(AutocompleteFilter):
    title = _('Customs Point')
    field_name = 'customspoint'

class BasisForDiscoveryFilter(AutocompleteFilter):
    title = _('Basis for Discovery')
    field_name = 'basisfordiscovery'

class MethodOfDiscoveryFilter(AutocompleteFilter):
    title = _('Method of Discovery')
    field_name = 'methodofdiscovery'

class WorkgroupFilter(AutocompleteFilter):
    title = _('Workgroup')
    field_name = 'methodofdiscovery'

class CustomsOfficerFilter(AutocompleteFilter):
    title = _('Customs Officer')
    field_name = 'customsofficer'


class AdministrationCodexFilter(admin.SimpleListFilter):
    title = _("Administration Codexes")
    parameter_name = "administration_codexes"

    def lookups(self, request, model_admin):
        """Return a list of tuples for the filter options."""
        codexes = AdministrationCodex.objects.all()
        return [(codex.id, codex.name) for codex in codexes]

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected codex(es)."""
        if self.value():
            # Filter for reports containing the selected codex
            return queryset.filter(administration_codexes__id=self.value()).distinct()
        return queryset

class ReportAdmin(nested_admin.NestedModelAdmin):    
    
    inlines = [StoredGoodInline, WitnessInline, AssignedTaskInline]
        

    actions = [export_report_to_excel,export_grouped_report]
 
    # Dine 'export_grouped_report' belli ulanyjylar un
    def get_actions(self, request):

        actions = super().get_actions(request)
        
        # List of usernames allowed to use 'export_grouped_report'
        allowed_usernames = ['admin', 'admin1']

        if request.user.username not in allowed_usernames:
            actions.pop('export_grouped_report', None)

        return actions

    def get_queryset(self, request):
        """
        Allow all users to see all records.
        """
        return super().get_queryset(request)


    def has_change_permission(self, request, obj=None):
        """
        Allow users to update only their own records or records related to them.
        Superusers can update all records.
        """
        if request.user.is_superuser:
            return True  # Superusers can edit all records
        
        if obj is None:  # Allows accessing the change list page
            return True
        
        # Check if the user is editing their own record
        if obj.user == request.user:
            return True
        
        # Check if the user is editing a record related to them through the UserProfile model
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if obj.user in user_profile.related_users.all():
                return True
        except UserProfile.DoesNotExist:
            return False  # If the user doesn't have a profile, they can't edit related users' records
        
        return False

    def save_model(self, request, obj, form, change):
        """
        Assign the current user to the user field during creation.
        """
        if not obj.pk:  # Only set the user on creation
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_username(self, obj):
        return obj.user.username if obj.user else '-'

    get_username.short_description = _('User')


    list_filter = (
                    'created_at',
                    'entry_exit_transit',
                    ('report_date', DateRangeFilter), 
                    CustomsOfficeFilter, 
                    CustomsPointFilter,
                    OriginCountryFilter,
                    DestinationCountryFilter,
                    BasisForDiscoveryFilter,
                    MethodOfDiscoveryFilter,
                    CustomsOfficerFilter,
                   )
    
    
    list_display_links = ('ish_toplum_number','protocol_number', 'customspoint','violation','formatted_report_date')
    list_display = (
                    'ish_toplum_number',
                    'formatted_report_date',
                    'customspoint', 
                    'violation',
                    'stored_goods_display',
                    'customsofficer',
                    'assigned_tasks_display',
                    'entry_exit_transit',
                    'from_country',
                    'to_country',
                    'customsoffice', 
                    'basisfordiscovery', 
                    'methodofdiscovery',
                    'protocol_number', 
                    'get_administration_codexes',
                    'language_of_work_conducted', 
                    'created_at',
                    'updated_at',
                    'get_username',
                    )
    search_fields = (
                    'ud_belgi',
                    'vehicle_brand__name',
                    'transport_company__name',
                    'protocol_number', 
                    'ish_toplum_number',
                    'report_date',
                    'customsoffice__name', 
                    'customspoint__name',
                    'violation__violation_type',
                    'violation__company_name',
                    'violation__phone',
                    'violation__violator_name',
                    'violation__violator_surname',
                    'violation__father_name',
                    'violation__date_of_birth',
                    'violation__passport_number',
                    'violation__nationality__name',
                    'violation__nationality__code',
                    'entry_exit_transit',
                    'from_country__name',
                    'from_country__code',
                    'to_country__name',
                    'to_country__code',
                    'customsofficer__name',
                    'customsofficer__surname',
                    'customsofficer__midname',
                    'customsofficer__position__name',
                    'customsofficer__militaryname__name',
                    'basisfordiscovery__name', 
                    'methodofdiscovery__name',
                    # 'reasonforruleviolation__name',
                    'administration_codexes__name',
                    'language_of_work_conducted',
                    'carnumber',
                    'stored_goods__product__name',
                    'stored_goods__amount',  # Search by amount
                    'stored_goods__unitofmeasurement__name',  # Search by unit of measurement
                    'stored_goods__note',  # Search by note (optional)
                    'user__username'
                    )
    
    readonly_fields = ('created_at', 'updated_at','get_username')
    filter_horizontal = ('administration_codexes',) 
    autocomplete_fields  = ['customsofficer','violation','from_country','to_country','transport_company'] 
    list_per_page = 5  # Display 100 items per page
    list_max_show_all = 100000  # Allow up to 500 items for "Show all"

    

    @admin.display(description=_('Assigned Task'))
    def assigned_tasks_display(self, obj):
        assigned_tasks = obj.assigned_tasks.all()
        tasks_list = [
            f"{task.workgroup} - {task.salnan_jerime} manat" 
            for task in assigned_tasks
        ]
        # Join tasks with line breaks or commas
        return ', '.join(tasks_list) if tasks_list else "No assigned tasks"


    @admin.display(description=_('Report date'))
    def formatted_report_date(self, obj):
        # Format the report_date field to 'dd/mm/yyyy'
        return obj.report_date.strftime('%d.%m.%Y') if obj.report_date else 'No date'

    @admin.display(description=_('Stored Goods with Images'))
    def stored_goods_display(self, obj):
        stored_goods = obj.stored_goods.all()  # Fetch associated stored goods
        goods_list = []
        max_images = 3  # Set the maximum number of images to display

        for stored_good in stored_goods:
            # Fetch only a limited number of images
            images = stored_good.images.all()[:max_images]

            # Create a string for images with anchor tags
            images_html = ''.join([
                f'<a href="{image.image.url}" target="_blank">'
                f'<img src="{image.image.url}" style="width:50px; height:50px; margin:2px; border:1px solid #ccc; border-radius:4px;" '
                f'title="{stored_good.product.name}" /></a>' 
                for image in images
            ])
            
            # If there are more images than the limit, add a "more images" link
            if stored_good.images.count() > max_images:
                images_html += f' <a href="#" title="View more images">+{stored_good.images.count() - max_images} more</a>'
            
            # Format the string for the stored good
            goods_list.append(
                f"<div style='margin-bottom: 5px;'>"
                f"<strong>{stored_good.product.name}:</strong> {stored_good.amount} {stored_good.unitofmeasurement}<br>"
                f"{images_html}"
                "</div>"
            )

        # Join the goods list with a line break for better separation
        return mark_safe('<br>'.join(goods_list)) if goods_list else "No stored goods"


    
    def get_administration_codexes(self, obj):
        return ", ".join([str(codex) for codex in obj.administration_codexes.all()])
    
    get_administration_codexes.short_description = _('Administration Codexes') 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'customsoffice':
            # Add logic for customsoffice autocomplete if needed
            pass
        elif db_field.name == 'customspoint':
            # Add logic for customspoint autocomplete based on customsoffice
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        # Fields to be displayed in the form
    fieldsets = (
        (_('General Information'), {
            'fields': (
                'ish_toplum_number',
                'protocol_number', 
                'report_date',
                'customsoffice', 
                'customspoint',
                'customsofficer', 
                'basisfordiscovery',
                'methodofdiscovery',
                # 'reasonforruleviolation',
                'language_of_work_conducted',
                'administration_codexes',
                'ud_belgi',
            )
        }),
        (_('Violation'), {
            'fields': ('violation', 
                       'entry_exit_transit',
                       'from_country', 
                       'to_country',
                       'vehicle_brand',
                       'carnumber',
                       'transport_company')
        }),
      
    )


    class Media:
        css = {
            'all': ('',)  # Include your custom CSS here
        }

admin.site.register(Report, ReportAdmin)




