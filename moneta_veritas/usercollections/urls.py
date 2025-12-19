# usercollections/urls.py
from django.urls import path
from . import views

app_name = 'usercollections'

urlpatterns = [
    path('my-collection/', views.MyCollectionView.as_view(), name='my_collection'),
    path('add-to-collection/', views.AddToCollectionView.as_view(), name='add_to_collection'),
    path('add/<str:item_type>/<int:item_id>/', views.add_item_to_collection, name='add_item'),
    path('edit/<int:pk>/', views.EditCollectionItemView.as_view(), name='edit_item'),
    path('remove/<int:pk>/', views.RemoveFromCollectionView.as_view(), name='remove_item'),
]