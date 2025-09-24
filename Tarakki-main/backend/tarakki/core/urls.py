from django.urls import path

from . import  views
urlpatterns = [
    path("",views.home,name="home"),
    path("signin",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path('dash', views.dashboard_home, name='dashboard_home'),
    path('roadmap/', views.dashboard_roadmap, name='dashboard_roadmap'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
    path('test/', views.dashboard_test, name='dashboard_test'),
    path('start_test/', views.start_test, name='start_test'),   # URL for starting the test
    path('submit_test/', views.submit_test, name='submit_test'), # URL for submitting the test
    path('interest-pred/', views.interest, name='interest'),
]