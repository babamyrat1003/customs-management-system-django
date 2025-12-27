from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions, viewsets, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from .models import (
    Witness, AdministrationCodex, Report
)
from customs_registry.models import (
    LettersForAction, Workgroup, StoredGood, StoredGoodImage, UnitOfMeasurement,
    ProductCategory, Product, TransportCompanyName, VehicleBrand, Country,
    Violation, ReasonForRuleViolation, CustomsOffice, CustomsPoint, CustomsOfficer,
    BasisForDiscovery, MethodOfDiscovery
)
from .serializers import (
    ReportsForActionSerializer, LettersForActionSerializer, WorkgroupSerializer,
    StoredGoodSerializer, StoredGoodImageSerializer, UnitOfMeasurementSerializer,
    ProductCategorySerializer, ProductSerializer, TransportCompanyNameSerializer,
    VehicleBrandSerializer, CountrySerializer, ViolationSerializer,
    ReasonForRuleViolationSerializer, MethodOfDiscoverySerializer, BasisForDiscoverySerializer,
    AdministrationCodexSerializer, CustomsOfficeSerializer, CustomsPointSerializer,
    CustomsOfficerSerializer, UserSerializer, GroupSerializer, PermissionSerializer
)
from .forms import ReportForm, WitnessForm

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PersonInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        passport_number = request.query_params.get('passport_number')
        if not passport_number:
            return Response({"detail": "passport_number is required"}, status=400)

        stored_goods_qs = StoredGood.objects.select_related('product', 'unitofmeasurement').prefetch_related('images')

        reports = Report.objects.filter(
            violation__passport_number=passport_number
        ).prefetch_related(
            Prefetch('stored_goods', queryset=stored_goods_qs),
            'administration_codexes',
            'assigned_tasks__workgroup'
        )

        data = []
        for report in reports:
            goods_serializer = StoredGoodSerializer(report.stored_goods.all(), many=True)
            codex_serializer = AdministrationCodexSerializer(report.administration_codexes.all(), many=True)

            assigned_task = getattr(report, 'assigned_tasks', None)
            assigned_task = assigned_task.first() if assigned_task else None
            salnan_jerime = assigned_task.salnan_jerime if assigned_task else None
            workgroup_name = assigned_task.workgroup.name if assigned_task else None

            data.append({
                "ish_toplum_number": report.ish_toplum_number,
                "report_date": report.report_date,
                "report_id": report.id,
                "stored_goods": goods_serializer.data,
                "administration_codexes": codex_serializer.data,
                "salnan_jerime": salnan_jerime,
                "workgroup_name": workgroup_name
            })

        return Response(data)


class StoredGoodViewSet(viewsets.ModelViewSet):
    queryset = StoredGood.objects.all()
    serializer_class = StoredGoodSerializer


class StoredGoodImageUploadViewSet(viewsets.ModelViewSet):
    queryset = StoredGoodImage.objects.all()
    serializer_class = StoredGoodImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomsOfficeViewSet(viewsets.ModelViewSet):
    queryset = CustomsOffice.objects.all()
    serializer_class = CustomsOfficeSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomsPointViewSet(viewsets.ModelViewSet):
    queryset = CustomsPoint.objects.all()
    serializer_class = CustomsPointSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomsOfficerViewSet(viewsets.ModelViewSet):
    queryset = CustomsOfficer.objects.all()
    serializer_class = CustomsOfficerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'midname','surname', 'militaryname__name', 'position__name']


class AdministrationCodexViewSet(viewsets.ModelViewSet):
    queryset = AdministrationCodex.objects.all()
    serializer_class = AdministrationCodexSerializer
    permission_classes = [permissions.IsAuthenticated]


class BasisForDiscoveryViewSet(viewsets.ModelViewSet):
    queryset = BasisForDiscovery.objects.all()
    serializer_class = BasisForDiscoverySerializer
    permission_classes = [permissions.IsAuthenticated]


class MethodOfDiscoveryViewSet(viewsets.ModelViewSet):
    queryset = MethodOfDiscovery.objects.all()
    serializer_class = MethodOfDiscoverySerializer
    permission_classes = [permissions.IsAuthenticated]


class ReasonForRuleViolationViewSet(viewsets.ModelViewSet):
    queryset = ReasonForRuleViolation.objects.all()
    serializer_class = ReasonForRuleViolationSerializer
    permission_classes = [permissions.IsAuthenticated]


class ViolationViewSet(viewsets.ModelViewSet):
    queryset = Violation.objects.all()
    serializer_class = ViolationSerializer
    permission_classes = [permissions.IsAuthenticated]


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]


class VehicleBrandViewSet(viewsets.ModelViewSet):
    queryset = VehicleBrand.objects.all()
    serializer_class = VehicleBrandSerializer
    permission_classes = [permissions.IsAuthenticated]


class TransportCompanyNameViewSet(viewsets.ModelViewSet):
    queryset = TransportCompanyName.objects.all()
    serializer_class = TransportCompanyNameSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class UnitOfMeasurementViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasurement.objects.all()
    serializer_class = UnitOfMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkgroupViewSet(viewsets.ModelViewSet):
    queryset = Workgroup.objects.all()
    serializer_class = WorkgroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class LettersForActionViewSet(viewsets.ModelViewSet):
    queryset = LettersForAction.objects.all()
    serializer_class = LettersForActionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportsForActionViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportsForActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    

def report_form_view(request):
    # Create the formset for Witnesses
    WitnessFormSet = modelformset_factory(Witness, form=WitnessForm, extra=1)

    # Handle the POST request
    if request.method == 'POST':
        print(request.POST)
        # Create the main report form and the formset
        report_form = ReportForm(request.POST)
        witness_formset = WitnessFormSet(request.POST)
        
        print(f"Report Form valid: {report_form.is_valid()}")
        print(f"Witness Formset valid: {witness_formset.is_valid()}")

        # Check if both the report form and the witness formset are valid
        if report_form.is_valid() and witness_formset.is_valid():
            # Save the report instance
            report = report_form.save()

            # Debug: Print the report ID to make sure it's being set correctly
            print(f"Report saved: {report.id}")

            # Manually set the report on each witness form
            for witness_form in witness_formset:
                if witness_form.is_valid():
                    # Save witness instance but don't commit yet
                    witness = witness_form.save(commit=False)
                    # Set the report foreign key
                    witness.report = report
                    # Save the witness instance
                    witness.save()

                    # Debug: Check the witness details
                    print(f"Saving witness: {witness.fullname}, associated with Report ID: {witness.report.id}")

            return redirect('report_form')  # Redirect to another page after success

    else:
        # If the request is a GET, create empty forms
        report_form = ReportForm()
        witness_formset = WitnessFormSet(queryset=Witness.objects.none())

    # Render the report form and the witness formset to the template
    return render(request, 'report_form.html', {
        'form': report_form,
        'witness_formset': witness_formset,
    })

@login_required(login_url='login')  
def main(request):
    return render(request, 'main.html')

def main_or_login(request):
    if request.user.is_authenticated:
        return render(request, 'main.html')
    else:
        return redirect('login')  

def get_customs_points(request):
    customsoffice_id = request.GET.get('customsoffice')
    if customsoffice_id:
        try:
            customs_points = CustomsPoint.objects.filter(customsoffice_id=customsoffice_id).values('id', 'name')
            return JsonResponse({'points': list(customs_points)})
        except CustomsPoint.DoesNotExist:
            return JsonResponse({'error': 'No customs points found.'}, status=404)
    return JsonResponse({'error': 'Customs office ID not provided'}, status=400)



