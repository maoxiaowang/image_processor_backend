from django.urls import path

from apiv1.views import auth as views

urlpatterns = [
    path('token/obtain/', views.TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/destroy/', views.TokenDestroyView.as_view(), name='token_destroy'),
    path('whoami/', views.WhoAmI.as_view(), name='whoami'),
]
