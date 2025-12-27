from ajax_select import register, LookupChannel
from customs_registry.models import CustomsOffice, CustomsPoint

@register('customspoints')
class CustomsPointLookup(LookupChannel):

    model = CustomsPoint

    def get_query(self, q, request):
        # Filter CustomsPoints based on the selected CustomsOffice
        office_id = request.GET.get('customsoffice')
        return self.model.objects.filter(customsoffice_id=office_id, name__icontains=q).order_by('name')

    def format_item_display(self, item):
        # Display name in the dropdown
        return f'{item.name}'
