from django.urls import path
from . import views
import uuid

app_name = 'pixelplan'

urlpatterns = [
    path('', views.index, name='index'),
    path('clients/', views.clients, name='clients'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/<uuid:pk>/', views.view_client, name='view_client'),
    path('clients/<uuid:pk>/update/', views.update_client, name='update_client'),
    path('clients/<int:pk>/delete/', views.delete_client, name='delete_client'),
    # Client Invoice URLs
    
    path('clients/<uuid:client_pk>/invoices/', views.list_invoices, name='list_invoices'),
    path('clients/<uuid:client_pk>/invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/<uuid:pk>/update/', views.update_invoice, name='update_invoice'),
    path('invoices/<uuid:pk>/delete/', views.delete_invoice, name='delete_invoice'),  
    path('invoices/', views.invoices, name='invoices'),   
    
    # Invoice URLs
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:pk>/', views.invoice_view, name='invoice_view'),
    path('invoices/<int:pk>/download/', views.invoice_download, name='invoice_download'),

    # URL for syncing clients with API
    path('clients/sync/', views.sync_clients_with_api, name='sync_clients_with_api'),
]
