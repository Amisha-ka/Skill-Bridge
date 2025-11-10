# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('find_matches/', views.find_matches, name='find_matches'),
    path('send_request/<int:receiver_id>/', views.send_request, name='send_request'),
    path('requests/', views.requests_page, name='requests_page'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('chat/', views.chat_view, name='chat'),
     path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('reviews/', views.review_page, name='review'),
    path('logout/', views.logout_confirm, name='logout'),
    path('logout/confirm/', views.logout_user, name='logout_user'),
    path('jobs/', views.job_list, name='job_list'),  
    path('skills/', views.skills, name='skills'),    


    ]
