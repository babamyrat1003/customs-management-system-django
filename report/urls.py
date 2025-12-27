from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView
from .views import LettersForActionViewSet, ReportsForActionViewSet, WorkgroupViewSet, StoredGoodViewSet, StoredGoodImageUploadViewSet, UnitOfMeasurementViewSet, ProductCategoryViewSet, ProductViewSet, TransportCompanyNameViewSet, VehicleBrandViewSet, CountryViewSet, ViolationViewSet, ReasonForRuleViolationViewSet, MethodOfDiscoveryViewSet, BasisForDiscoveryViewSet, AdministrationCodexViewSet, CustomsOfficeViewSet, CustomsPointViewSet, CustomsOfficerViewSet, get_customs_points
from rest_framework.routers import DefaultRouter
from report.views import login_view, logout_view, UserViewSet, GroupViewSet, PermissionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.decorators.csrf import csrf_exempt


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'customs-offices', CustomsOfficeViewSet, basename='customs-office')
router.register(r'customs-points', CustomsPointViewSet, basename='customs-point')
router.register(r'customs-officers', CustomsOfficerViewSet, basename='customs-officer')
router.register(r'administration_codexes', AdministrationCodexViewSet, basename='administration_codex')
router.register(r'basisfordiscoveries', BasisForDiscoveryViewSet , basename='basisfordiscovery')
router.register(r'methodofdiscoveries', MethodOfDiscoveryViewSet , basename='methodofdiscovery')
router.register(r'reasonforruleviolations', ReasonForRuleViolationViewSet , basename='reasonforruleviolation')
router.register(r'violations', ViolationViewSet , basename='violation')
router.register(r'countries', CountryViewSet , basename='country')
router.register(r'vehicle-brands', VehicleBrandViewSet , basename='vehicle-brand')
router.register(r'transport-companies', TransportCompanyNameViewSet , basename='transport-company')
router.register(r'products', ProductViewSet , basename='product')
router.register(r'product-categories', ProductCategoryViewSet , basename='product-category')
router.register(r'unitofmeasurements', UnitOfMeasurementViewSet , basename='unitofmeasurement')
router.register(r'stored-goods', StoredGoodViewSet)
router.register(r'stored-good-images', StoredGoodImageUploadViewSet)
router.register(r'workgroups', WorkgroupViewSet, basename='workgroup')
router.register(r'letters-for-actions', LettersForActionViewSet, basename='letters-for-action')
router.register(r'total-report-data', ReportsForActionViewSet, basename='total-report-data')
 
 
urlpatterns = [
    path('api/auth/login_forbirulgam/', csrf_exempt(views.login_view), name='login'), 
    
    path('api/auth/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

   
    path("api/person-info/", views.PersonInfoAPIView.as_view(), name="person-info"),

    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    
    path('api/', include(router.urls)),

    path('', views.main_or_login, name='home'), 
    path('main/', views.main, name='main'),  
    path('get-customs-points/', get_customs_points, name='get_customs_points'),
    path('login/', LoginView.as_view(), name='login'),
    path('report/form/', views.report_form_view, name='report_form'),    
    
]
