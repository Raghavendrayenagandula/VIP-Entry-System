from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('visitor/add/', views.add_visitor, name='add_visitor'),
    path('visitor/pass/<uuid:pass_id>/', views.view_pass, name='view_pass'),
    path('scanner/', views.scanner_interface, name='scanner'),
    path('api/process-scan/', views.process_scan, name='process_scan'),
    
]