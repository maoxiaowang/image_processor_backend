from django.urls import path, include

urlpatterns = [
    path('auth/', include('apiv1.urls.auth')),
    path('image/', include('apiv1.urls.image'))
]
