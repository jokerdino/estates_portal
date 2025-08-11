# tables.py
import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from .models import LeaseApplication, RentPayment, Deposit, Employee, LandLord


class LeaseApplicationTable(tables.Table):
    view = tables.Column(empty_values=(), orderable=False)
    edit = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = LeaseApplication
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            "class": "table table-bordered table-striped table-hover",
            "id": "leaseApplicationTable",
        }
        # fields = ("name", "age")  # only include data columns

    def render_view(self, record):
        url = reverse("lease_detail", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-info" href="{}">View</a>', url)

    def render_edit(self, record):
        url = reverse("lease_edit", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-warning" href="{}">Edit</a>', url)


# class RentPaymentTable(tables.Table):
#     class Meta:
#         model = RentPayment
#         template_name = "django_tables2/bootstrap5.html"
#         attrs = {
#             "class": "table table-bordered table-striped table-hover",
#             "id": "rentPaymentTable",
#         }
class RentPaymentTable(tables.Table):
    select = tables.CheckBoxColumn(
        accessor="pk",
        orderable=False,
        attrs={
            "th__input": {"id": "select-all"},  # Used to implement "select all"
        },
    )

    class Meta:
        model = RentPayment
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "select",
            "lease.type_of_lease",
            "lease.lease_start_date",
            "rent_start_date",
            "rent_end_date",
            "amount",
            "status",
        )
        attrs = {
            "class": "table table-bordered table-striped table-hover",
            "id": "rentPaymentTable",
        }


class DepositTable(tables.Table):
    view = tables.Column(empty_values=(), orderable=False)
    edit = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = Deposit
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            "class": "table table-bordered table-striped table-hover",
            "id": "leaseApplicationTable",
        }
        # fields = ("name", "age")  # only include data columns

    def render_view(self, record):
        url = reverse("deposit_detail", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-info" href="{}">View</a>', url)

    def render_edit(self, record):
        url = reverse("deposit_update", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-warning" href="{}">Edit</a>', url)


class EmployeeTable(tables.Table):
    view = tables.Column(empty_values=(), orderable=False)
    edit = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = Employee
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            "class": "table table-bordered table-striped table-hover",
            "id": "leaseApplicationTable",
        }
        # fields = ("name", "age")  # only include data columns

    def render_view(self, record):
        url = reverse("employee_detail", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-info" href="{}">View</a>', url)

    def render_edit(self, record):
        url = reverse("employee_update", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-warning" href="{}">Edit</a>', url)


class LandlordTable(tables.Table):
    view = tables.Column(empty_values=(), orderable=False)
    edit = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = LandLord
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            "class": "table table-bordered table-striped table-hover",
            "id": "leaseApplicationTable",
        }
        # fields = ("name", "age")  # only include data columns

    def render_view(self, record):
        url = reverse("landlord_detail", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-info" href="{}">View</a>', url)

    def render_edit(self, record):
        url = reverse("landlord_update", args=[record.pk])
        return format_html('<a class="btn btn-sm btn-warning" href="{}">Edit</a>', url)
