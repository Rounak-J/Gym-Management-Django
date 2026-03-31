from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_member, name='add_member'), # New line
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('upgrade/<int:member_id>/', views.upgrade_membership, name='upgrade_membership'),
]