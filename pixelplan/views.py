from django.shortcuts import render, get_object_or_404, redirect
from .models import Client, Invoice
from .forms import ClientForm, InvoiceForm
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import FileResponse

def index(request):
    return render(request, 'pixelplan/dashboard.html')


# Update Client - Adjust this logic to fetch and pass the form to the template
def view_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    invoices = Invoice.objects.filter(client=client)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)  # Bind form with POST data
        if form.is_valid():
            form.save()  # Save form data if valid
            return redirect('clients')
    else:
        form = ClientForm(instance=client)  # Populate form with existing client data
    invoice_form = InvoiceForm(instance=client)
    return render(request, 'pixelplan/client_view.html', {'client': client, 'invoices': invoices, 'form': form, 'invoice_form': invoice_form})


# Function to sync clients with the API
def sync_clients_with_api():
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

        return True
    except Exception as e:
        return False

# List Clients
def clients(request):
    clients = Client.objects.all()
    return render(request, 'pixelplan/clients.html', {'clients': clients})

# Create Client
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clients')
    else:
        form = ClientForm()
    return render(request, 'pixelplan/create_client.html', {'form': form})

# Update Client
def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('clients')
    else:
        form = ClientForm(instance=client)
    return render(request, 'pixelplan/client_view.html', {'form': form})

# Delete Client
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('clients')
    return render(request, 'pixelplan/delete_client.html', {'client': client})



# List Invoices (Under a Specific Client)

@login_required
def list_invoices(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    invoices = Invoice.objects.filter(creator=request.user)
    return render(request, 'pixelplan/invoices.html', {'invoices': invoices, 'client': client})

# Create Invoice
def create_invoice(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.creator = request.user
            invoice.client = client
            invoice.save()

            # Sending email with attachment
            email = EmailMessage(
                f"Invoice {invoice.name}",
                f"Dear {invoice.client.name}, find the attached invoice.",
                settings.DEFAULT_FROM_EMAIL,
                [invoice.client.email],
            )
            email.attach(invoice.file.name, invoice.file.read(), 'application/pdf')
            email.send()

            # Redirect to view client details
            return redirect('view_client', pk=client.pk)
    else:
        form = InvoiceForm()
    return render(request, 'pixelplan/client_view.html', {'form': form, 'client': client})

# Update Invoice
def update_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES, instance=invoice)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Invoice updated successfully'}, status=200)
        else:
            # Handle invalid form case. This is a simplified example.
            # In production, consider adding form error details to the response.
            return JsonResponse({'error': 'Form is not valid'}, status=400)
    else:
        # For a GET request, return an empty response or redirect as this view is for updates via AJAX.
        return JsonResponse({'error': 'GET request not allowed'}, status=405)

# Delete Invoice
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    client_pk = invoice.client.pk
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice successfully deleted!')
        return redirect('view_client', pk=client_pk)
    return render(request, 'pixelplan/delete_invoice.html', {'invoice': invoice})


# All Clients invoices by Users

@login_required
def invoices(request):
    form = InvoiceForm()  # No need to pass user here as we removed the filtering
    invoices = Invoice.objects.filter(creator=request.user)
    return render(request, 'pixelplan/invoices.html', {'invoices': invoices, 'form': form})


@login_required
def invoice_create(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.creator = request.user
            invoice.save()
            
            # The email sending logic is within the save method of the Invoice model.
            # It will check the `send_email` flag and proceed accordingly.

            # Sending back a success response
            return JsonResponse({"success": True, "message": "Invoice successfully created!"}, status=200)
        else:
            # Form is not valid, send back an error response
            return JsonResponse({"error": form.errors.as_json()}, status=400)
    else:
        # Not a POST request
        return JsonResponse({"error": "Invalid request"}, status=400)



@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, creator=request.user)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES, instance=invoice)
        if form.is_valid():
            updated_invoice = form.save()
            return JsonResponse({
                'message': 'Invoice successfully updated!',
                'invoice': {
                    'id': updated_invoice.id,
                    'name': updated_invoice.name,
                    'status': updated_invoice.status,
                    'client_id': updated_invoice.client.id,
                    'client_name': f"{updated_invoice.client.given_name} {updated_invoice.client.family_name}",
                    'send_email': updated_invoice.send_email,
                }
            }, status=200)
        else:
            return JsonResponse({
                'errors': form.errors.get_json_data(),
                'message': 'There was a problem updating the invoice.'
            }, status=400)

    elif request.method == 'GET':
        # Get the invoice data and client list for dropdown
        invoice_data = {
            'id': invoice.id,
            'name': invoice.name,
            'status': invoice.status,
            'client_id': invoice.client.id,
            'client_name': f"{invoice.client.given_name} {invoice.client.family_name}",
            'send_email': invoice.send_email,
        }
        clients = list(Client.objects.values('id', 'given_name', 'family_name'))
        return JsonResponse({
            'invoice': invoice_data,
            'clients': clients
        })

    else:
        # Redirect or render a form with errors if it's neither GET nor POST
        form = InvoiceForm(instance=invoice)
        return render(request, 'pixelplan/invoices.html', {'form': form})

@login_required
def invoice_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, creator=request.user)
    return render(request, 'pixelplan/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_download(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, creator=request.user)
    file_path = invoice.file.path
    response = FileResponse(open(file_path, 'rb'))
    return response

@login_required
@require_POST
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, creator=request.user)
    invoice.delete()
    return JsonResponse({'success': True, 'message': 'Invoice successfully deleted!'})


