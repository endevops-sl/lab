from django import forms
from .models import Client, Invoice

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'id', 'given_name', 'family_name', 'email',
            'company_id', 'status', 'invite_url',
            'avatar_image_url', 'custom_fields'
        ]
        widgets = {
            'custom_fields': forms.Textarea(attrs={'cols': 40, 'rows': 5, 'class': 'form-control'}),
            'invite_url': forms.URLInput(attrs={'placeholder': 'https://', 'class': 'form-control'}),
            'avatar_image_url': forms.URLInput(attrs={'placeholder': 'https://', 'class': 'form-control'}),
            # Other fields will use their default widgets but you can add 'class': 'form-control' if needed
        }

class InvoiceForm(forms.ModelForm):
    current_file_path = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Invoice
        fields = ['name', 'status', 'client', 'file', 'send_email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf, application/vnd.ms-excel'
            }),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all()
        self.fields['client'].widget.attrs.update({'class': 'form-select'})
        # If the Invoice model has a 'creator' field, you would initialize it here.
        # If not, remove references to 'creator'.
        # Assuming there's no 'creator' field on the form as it's managed in the view:
        # self.fields['creator'].initial = user.id if user is not None else None
        # self.fields['creator'].widget = forms.HiddenInput()

        # Apply Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-select'
