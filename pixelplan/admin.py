from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html  # Import format_html
from .models import Client, Invoice
import requests


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    change_list_template = "admin/clients_change_list.html"
    list_display = ('id', 'given_name', 'family_name', 'email', 'company_id', 'status', 'creation_method', 'sync_actions_html')
    list_filter = ('status', 'company_id', 'creation_method')
    search_fields = ('given_name', 'family_name', 'email', 'id')
    readonly_fields = ('custom_fields', 'id', 'company_id', 'status', 'creation_method', 'created_at', 'first_login_date', 'last_login_date', 'invite_url', 'avatar_image_url')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync_clients/', self.admin_site.admin_view(self.sync_clients), name='sync_clients'),
        ]
        return custom_urls + urls

    def sync_clients(self, request):
        try:
            url = "https://api.copilot.com/v1/clients?limit=100"
            headers = {
                "accept": "application/json",
                "X-API-KEY": "f213e6779b484f3fa975fcae17343fc8.3c8838d9c7d1fee2"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes (4xx or 5xx)

            clients_data = response.json().get('data', [])

            for client_data in clients_data:
                defaults = {
                    'given_name': client_data.get('givenName', ''),
                    'family_name': client_data.get('familyName', ''),
                    'email': client_data.get('email', ''),
                    'company_id': client_data.get('companyId', ''),
                    'status': client_data.get('status', ''),
                    'invite_url': client_data.get('inviteUrl', ''),
                    'avatar_image_url': client_data.get('avatarImageUrl', ''),
                    'first_login_date': client_data.get('firstLoginDate', None),
                    'last_login_date': client_data.get('lastLoginDate', None),
                    'creation_method': client_data.get('creationMethod', ''),
                    'custom_fields': client_data.get('customFields', {}),
                }
                # Assuming Client model has 'id' field
                client_obj, created = Client.objects.update_or_create(id=client_data.get('id'), defaults=defaults)

            self.message_user(request, "Clients successfully synced with API.", level='success')
        except Exception as e:
            self.message_user(request, f"Failed to sync clients: {e}", level='error')

        return HttpResponseRedirect("../")


    def sync_actions_html(self, obj):
        return format_html('<a class="button" href="{}">Sync Now</a>', self.sync_clients_url())
    sync_actions_html.short_description = 'Sync Actions'

    def sync_clients_url(self):
        return 'sync_clients/'

    def response_add(self, request, obj, post_url_continue=None):
        """
        Overrides the response after a new Client instance is successfully added.
        Redirects to the change page for the newly created Client instance.
        """
        if obj.pk:
            self.message_user(request, f"Successfully added '{obj}'.", level=messages.SUCCESS)
            return HttpResponseRedirect(reverse('admin:pixelplan_client_change', args=[obj.pk]))
        else:
            return super().response_add(request, obj, post_url_continue)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'status', 'shared_on', 'client_display', 'send_email')
    list_filter = ('status', 'shared_on', 'send_email')
    search_fields = ('name', 'client__given_name', 'client__family_name', 'client__id')
    date_hierarchy = 'shared_on'
    ordering = ('-shared_on',)

    # Specify which fields are displayed in the form
    fields = ('name', 'creator', 'status', 'client', 'file', 'send_email')

    def client_display(self, obj):
        return f"{obj.client.given_name} {obj.client.family_name}"
    client_display.short_description = "Client"

