from django import forms


from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from .models import LeaseApplication, LandLord, Employee, Deposit


class DepositForm(forms.ModelForm):
    date_of_payment = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=True
    )

    class Meta:
        model = Deposit
        fields = [
            "lease",
            "amount",
            # "current_status",
            "utr_number",
            "date_of_payment",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()

        self.fields["lease"].queryset = LeaseApplication.objects.filter(
            type_of_lease__in=["company", "joint"],
            lease_end_date__gte=today,
            deposit__isnull=True,
        )


class DepositRefundForm(forms.ModelForm):
    date_of_refund = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    class Meta:
        model = Deposit
        fields = [
            "lease",
            "amount",
            # "current_status",
            "utr_number",
            "date_of_payment",
            "current_status",
            "mode_of_refund",
            "refund_instrument_number",
            "date_of_refund",
            "refund_payment_document",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()

        # Base filter: company/joint & active
        base_filter = Q(
            type_of_lease__in=["company", "joint"],
            lease_end_date__gte=today,
            deposit__isnull=True,
        )

        # If editing an existing Deposit with lease attached
        current_lease = (
            self.instance.lease if self.instance and self.instance.pk else None
        )

        if current_lease:
            self.fields["lease"].queryset = LeaseApplication.objects.filter(
                base_filter | Q(pk=current_lease.pk)
            ).distinct()
        else:
            self.fields["lease"].queryset = LeaseApplication.objects.filter(base_filter)


class LeaseApplicationForm(forms.ModelForm):
    success_url = reverse_lazy("lease_list")

    # status = forms.ChoiceField()
    lease_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )
    lease_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )

    class Meta:
        model = LeaseApplication

        # fields = "__all__"
        fields = [
            "type_of_lease",
            "lease_start_date",
            "lease_end_date",
            "lease_deposit",
            "rent",
            "remarks",
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("lease_start_date")
        end_date = cleaned_data.get("lease_end_date")

        if start_date and end_date and start_date > end_date:
            self.add_error("lease_end_date", "End date must be after start date.")


class EmployeeForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.required = False

    class Meta:
        model = Employee
        fields = [
            "employee_number",
            "employee_name",
            "employee_designation",
            "office_code",
            "department",
            "office_name",
            "housing_loan",
        ]


class LandLordForm(forms.ModelForm):
    class Meta:
        model = LandLord
        fields = [
            "landlord_code",
            "landlord_name",
            "pan_number",
            "bank_account_number",
            "bank_ifsc_code",
            "bank_name",
            "bank_branch_name",
            "bank_account_details",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["landlord_code"].widget.attrs.update(
            {
                "hx-get": reverse("get_landlord"),
                "hx-target": "#landlord-section",
                "hx-trigger": "blur",
            }
        )


class RentPaymentPaidForm(forms.Form):
    date_of_payment = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    utr_number = forms.CharField(max_length=100, required=False)
    remarks = forms.CharField(max_length=100, required=False)
