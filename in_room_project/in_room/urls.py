from django.urls import path
from . import views

urlpatterns = [
    path('input_page/', views.InputPageView.as_view(), name='input_page'),
    path('status/', views.StatusPageView.as_view(), name='status_page'),
    path('record_entry/', views.RecordEntryView.as_view(), name='record_entry'),
]