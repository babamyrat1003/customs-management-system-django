from django.contrib.auth.models import User, Group, Permission
from customs_registry.models import  LettersForAction, Workgroup, StoredGood, StoredGoodImage, UnitOfMeasurement, ProductCategory, Product, TransportCompanyName, VehicleBrand, Country, Violation, ReasonForRuleViolation, MethodOfDiscovery, CustomsOffice, CustomsPoint, CustomsOfficer, AdministrationCodex, BasisForDiscovery
from rest_framework import serializers
from .models import AssignedLetter, Report, AssignedTask

class StoredGoodImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredGoodImage
        fields = ['id', 'image', 'description', 'uploaded_at']

class StoredGoodSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    images = StoredGoodImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = StoredGood
        fields = ['id', 'product', 'product_name', 'amount', 'unitofmeasurement', 'note', 'created_at', 'updated_at', 'images']

class AdministrationCodexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrationCodex
        fields = ['id', 'name', 'description']

class ReportSerializer(serializers.ModelSerializer):
    stored_goods = StoredGoodSerializer(many=True, read_only=True)
    administration_codexes = AdministrationCodexSerializer(many=True, read_only=True)
    
    class Meta:
        model = Report
        fields = ['ish_toplum_number', 'report_date', 'report_id', 'stored_goods', 'administration_codexes', 'salnan_jerime', 'workgroup_name']
        
class AdministrationCodexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrationCodex
        fields = '__all__'


class AssignedTaskSerializer(serializers.ModelSerializer):
    workgroup_name = serializers.CharField(source='workgroup.name', read_only=True)

    class Meta:
        model = AssignedTask
        fields = ['salnan_jerime', 'workgroup_name']


class ReportSerializer(serializers.ModelSerializer):
    stored_goods = StoredGoodSerializer(many=True, read_only=True)
    administration_codexes = AdministrationCodexSerializer(many=True, read_only=True)
    assigned_tasks = AssignedTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'ish_toplum_number',
            'report_date',
            'stored_goods',
            'administration_codexes',
            'assigned_tasks'
        ]


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']

class CustomsOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsOffice
        fields = '__all__'

class CustomsPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsPoint
        fields = '__all__'

class CustomsOfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsOfficer
        fields = '__all__'
        depth = 1  # This will include full objects for ForeignKeys

class AdministrationCodexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrationCodex
        fields = '__all__'

class BasisForDiscoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = BasisForDiscovery
        fields = '__all__'

class MethodOfDiscoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = MethodOfDiscovery
        fields = '__all__'


class ReasonForRuleViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonForRuleViolation
        fields = '__all__'

class ViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violation
        fields = '__all__'
        depth = 1

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class VehicleBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleBrand
        fields = '__all__'

class TransportCompanyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportCompanyName
        fields = '__all__'

class TransportCompanyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportCompanyName
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 1

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class UnitOfMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasurement
        fields = '__all__'

class StoredGoodImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredGoodImage
        fields = ['id', 'stored_good', 'image', 'description', 'uploaded_at']

#class StoredGoodSerializer(serializers.ModelSerializer):
    #images = StoredGoodImageSerializer(many=True, read_only=True)  # Nested images

    #class Meta:
        #model = StoredGood
        #fields = ['id', 'product', 'amount', 'unitofmeasurement', 'note', 'created_at', 'updated_at', 'report', 'images']

class WorkgroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workgroup
        fields = '__all__'

class LettersForActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LettersForAction
        fields = '__all__'

class ReportsForActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


        