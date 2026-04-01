from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_member, name='add_member'), # New line
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('upgrade/<int:member_id>/', views.upgrade_membership, name='upgrade_membership'),
    path('workouts/', views.workout_plans, name='workout_plans'),
    path('benefits/', views.tier_benefits, name='tier_benefits'),
    path('archive/', views.member_archive, name='member_archive'),
    path('restore/<int:member_id>/', views.restore_member, name='restore_member'),
    path('members/', views.members_list, name='members_list'),
    path('edit/<int:member_id>/', views.edit_member, name='edit_member'),
]
