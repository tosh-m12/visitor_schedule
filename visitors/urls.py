from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_visitor, name='add_visitor'),
    path('cancel/<int:id>/', views.cancel_visitor, name='cancel_visitor'),
    path('edit/<int:id>/', views.edit_visitor, name='edit_visitor'),
    path('settings/', views.settings_view, name='settings'),
]
