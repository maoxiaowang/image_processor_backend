from django.urls import path
from apiv1.views import image as views

urlpatterns = [
    path('images/', views.ListCreateImageView.as_view(), name='images'),
    path('image/<int:pk>/', views.RetrieveUpdateDestroyImageView.as_view(), name='image'),
    path('images/<comma_ints:image_ids>/delete/', views.DeleteMultiImageView.as_view(), name='delete_images'),

    path('image/<int:pk>/<str:action>/', views.ProcessImageView.as_view(), name='process_image'),
    path('generation/<int:pk>/elevate/', views.ElevateGenerationImageView.as_view(), name='elevate_image')
]
