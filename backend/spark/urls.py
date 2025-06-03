# spark/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='spark-index'),
    path('dataset-a/', views.dataset_a_view, name='dataset-a'),
     path('dataset-b/', views.dataset_b_view, name='dataset-b'),
     path('comparer/', views.comparer_datasets),
]
