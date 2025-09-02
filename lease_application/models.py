from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.conf import settings
from auditlog.registry import auditlog

DESIGNATION = (
    ("assistant", "Assistant"),
    ("senior_assistant", "Senior Assistant"),
    ("admin_officer", "Administrative Officer"),
    ("assistant_manager", "Assistant Manager"),
    ("deputy_manager", "Deputy Manager"),
    ("manager", "Manager"),
    ("chief_manager", "Chief Manager"),
    ("deputy_general_manager", "Deputy General Manager"),
    ("general_manager", "General Manager"),
    ("executive_director", "Executive Director"),
    ("cmd", "CMD"),
)
TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))


# Create your models here.
class Employee(models.Model):
    employee_number = models.IntegerField(unique=True)
    employee_name = models.CharField(max_length=100)
    employee_mobile_number = models.CharField(max_length=100, null=True, blank=True)
    employee_designation = models.CharField(
        choices=DESIGNATION, max_length=100, null=True, blank=True
    )
    office_code = models.CharField(max_length=100, null=True)
    department = models.CharField(max_length=100)
    office_name = models.CharField(max_length=100, null=True)
    housing_loan = models.BooleanField(
        "Whether housing loan was availed?",
        choices=TRUE_FALSE_CHOICES,
        default=False,
        null=True,
    )
    housing_loan_location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("employee_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.employee_name} - {self.employee_number}"


class LandLord(models.Model):
    # lease = models.ForeignKey(LeaseApplication, null=True, on_delete=models.SET_NULL)
    landlord_name = models.CharField(max_length=100)
    landlord_code = models.CharField(unique=True, max_length=100, blank=True, null=True)
    landlord_mobile_number = models.CharField(max_length=100, null=True, blank=True)
    landlord_email_address = models.CharField(max_length=100, null=True, blank=True)

    landlord_residential_address = models.TextField(null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_branch_name = models.CharField(max_length=100, null=True, blank=True)
    bank_ifsc_code = models.CharField(null=True, max_length=100, blank=True)
    bank_account_number = models.CharField(null=True, max_length=100, blank=True)

    pan_number = models.CharField(max_length=100, null=True, blank=True)
    bank_account_details = models.FileField(
        upload_to="bank_account_details", null=True, blank=True
    )

    legal_heir = models.BooleanField(
        "Whether legal heir", default=False, null=True, blank=True
    )
    general_poa = models.BooleanField(
        "Whether General power of attorney is available",
        default=False,
        null=True,
        blank=True,
    )

    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_landlord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_landlord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )  # ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("landlord_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"{self.landlord_code} - {self.landlord_name}"


class LeaseApplication(models.Model):
    LEASE_TYPE = (
        ("company", "Company lease"),
        ("personal", "Personal lease"),
        ("joint", "Joint lease"),
    )

    type_of_lease = models.CharField(max_length=100, choices=LEASE_TYPE)

    primary_employee = models.ForeignKey(
        Employee, null=True, on_delete=models.SET_NULL, related_name="primary_leases"
    )
    joint_employee = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="joint_leases",
    )
    landlord = models.ForeignKey(
        LandLord, null=True, on_delete=models.SET_NULL, related_name="landlord"
    )
    #    rent_amount = models.IntegerField(null=True)

    lease_start_date = models.DateField()
    lease_end_date = models.DateField()

    date_of_termination = models.DateField(null=True)
    lease_deposit = models.IntegerField()
    rent = models.IntegerField()
    carpet_area = models.IntegerField(default=0, null=True, blank=True)
    address_of_property = models.TextField(max_length=1000, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    status = models.CharField(
        default="pending", null=True
    )  # pending, approved, expired, etc

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_lease",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_lease",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("lease_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.get_type_of_lease_display()}-{self.primary_employee}-{self.landlord}-{self.lease_start_date:%d/%m/%Y}-{self.lease_end_date:%d/%m/%Y}"


class Deposit(models.Model):
    lease = models.ForeignKey(LeaseApplication, null=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    current_status = models.CharField(
        choices=(
            ("paid", "Paid to landlord"),
            ("received", "Deposit received from landlord"),
        ),
        default="paid",
        max_length=100,
    )
    employee_deposit_share = models.BooleanField(default=False, null=True, blank=True)
    employee_deposit_share_amount = models.IntegerField(null=True, blank=True)
    employee_deposit_share_date = models.DateField(null=True, blank=True)
    employee_deposit_share_utr_number = models.CharField(
        max_length=100, null=True, blank=True
    )
    employee_deposit_share_documents = models.FileField(null=True, blank=True)

    utr_number = models.CharField(max_length=100)
    date_of_payment = models.DateField()

    mode_of_refund = models.CharField(
        choices=(("cheque", "Cheque"), ("cash", "Cash"), ("neft", "NEFT")),
        max_length=100,
        blank=True,
        null=True,
    )
    refund_instrument_number = models.CharField(
        "UTR number / Cheque number", max_length=100, blank=True, null=True
    )
    date_of_refund = models.DateField(blank=True, null=True)
    refund_payment_document = models.FileField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_deposit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_deposit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("deposit_detail", kwargs={"pk": self.pk})


class RentPayment(models.Model):
    lease = models.ForeignKey(LeaseApplication, null=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    rent_start_date = models.DateField(null=True)
    rent_end_date = models.DateField(null=True)
    payee_name = models.CharField(max_length=100)
    payee_account_number = models.CharField(max_length=100, null=True, blank=True)
    payee_ifsc = models.CharField(max_length=100, null=True, blank=True)
    payee_type = models.CharField(
        max_length=20, choices=[("landlord", "Landlord"), ("employee", "Employee")]
    )

    date_of_payment = models.DateField(null=True)
    utr_number = models.CharField(max_length=100)
    remarks = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_rent_payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_rent_payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("rent_payment_detail", kwargs={"pk": self.pk})


class Eligibility(models.Model):
    amount = models.IntegerField()
    designation = models.CharField(choices=DESIGNATION, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_eligibility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_eligibility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("eligibility_detail", kwargs={"pk": self.pk})


auditlog.register(LeaseApplication)
auditlog.register(LandLord)
auditlog.register(Employee)
auditlog.register(RentPayment)
auditlog.register(Deposit)
auditlog.register(Eligibility)
