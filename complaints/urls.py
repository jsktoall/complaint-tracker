from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_complaint, name='register_complaint'),
    path('unsolved/', views.unsolved_complaints, name='unsolved_complaints'),
    path('confirm_solved/<int:complaint_id>/', views.confirm_solve, name='confirm_solve'),
    path('mark_solved/<int:complaint_id>/', views.mark_solved, name='mark_solved'),
    path('export/<str:period>/', views.export_complaints, name='export_complaints'),
    path('solved/', views.solved_complaints, name='solved_complaints'),  # ✅ Add this if it's missing
]
