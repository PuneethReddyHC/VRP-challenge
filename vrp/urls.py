from django.urls import path

from . import views

app_name = 'vrp'
urlpatterns = [
    path('', views.index, name='index'),
    path('problem_settings/', views.problem_setting, name='problem_settings'),
    path('problem_solution/', views.problem_solution, name='problem_solution'),
    path('create_problem/', views.create_problem, name='create_problem'),
]