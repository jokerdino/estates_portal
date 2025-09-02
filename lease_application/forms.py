from django import forms


from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from .models import LeaseApplication, LandLord, Employee, Deposit


class DepositForm(forms.ModelForm):
    date_of_payment = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=True
    )
    employee_deposit_share_date = forms.DateField(
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
            "employee_deposit_share",
            "employee_deposit_share_amount",
            "employee_deposit_share_date",
            "employee_deposit_share_utr_number",
            "employee_deposit_share_documents",
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
    employee_deposit_share_date = forms.DateField(
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
            "employee_deposit_share",
            "employee_deposit_share_amount",
            "employee_deposit_share_date",
            "employee_deposit_share_utr_number",
            "employee_deposit_share_documents",
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

    date_of_termination = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
    )

    class Meta:
        model = LeaseApplication

        # fields = "__all__"
        fields = [
            "type_of_lease",
            "lease_start_date",
            "lease_end_date",
            "date_of_termination",
            "carpet_area",
            "address_of_property",
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
            "employee_mobile_number",
            "employee_designation",
            "office_code",
            "department",
            "office_name",
            "housing_loan",
            "housing_loan_location",
        ]

    def clean(self):
        cleaned_data = super().clean()
        housing_loan = cleaned_data.get("housing_loan")
        housing_loan_location = cleaned_data.get("housing_loan_location")

        if housing_loan and not housing_loan_location:
            self.add_error(
                "housing_loan_location",
                "Housing loan location is required if housing loan is availed.",
            )

        return cleaned_data


class LandLordForm(forms.ModelForm):
    class Meta:
        model = LandLord
        fields = [
            "landlord_code",
            "landlord_name",
            "landlord_mobile_number",
            "landlord_email_address",
            "landlord_residential_address",
            "pan_number",
            "legal_heir",
            "general_poa",
            "bank_account_number",
            "bank_ifsc_code",
            "bank_name",
            "bank_branch_name",
            "bank_account_details",
            "remarks",
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
