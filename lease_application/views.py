import calendar
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse

from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict

from django_tables2.views import SingleTableView

from .models import (
    LeaseApplication,
    LandLord,
    Eligibility,
    RentPayment,
    Deposit,
    Employee,
)
from .forms import (
    LeaseApplicationForm,
    LandLordForm,
    EmployeeForm,
    DepositRefundForm,
    DepositForm,
    RentPaymentPaidForm,
)

# from .forms import RentPaymentPaidForm
from .tables import (
    LeaseApplicationTable,
    RentPaymentTable,
    DepositTable,
    EmployeeTable,
    LandlordTable,
)
import django_tables2 as tables


# Create your views here.
class DepositCreateView(LoginRequiredMixin, CreateView):
    model = Deposit
    form_class = DepositForm
    template_name = "deposits/deposit_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user  # Both at creation
        return super().form_valid(form)


class DepositUpdateView(LoginRequiredMixin, UpdateView):
    model = Deposit
    form_class = DepositRefundForm
    template_name = "deposits/deposit_form.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # Only update this
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # Only update this
        return super().form_valid(form)


class LandlordUpdateView(LoginRequiredMixin, UpdateView):
    model = LandLord
    form_class = LandLordForm
    template_name = "landlords/landlord_form.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # Only update this
        return super().form_valid(form)


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user  # Both at creation
        return super().form_valid(form)


class LandlordCreateView(LoginRequiredMixin, CreateView):
    model = LandLord
    form_class = LandLordForm
    template_name = "landlords/landlord_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user  # Both at creation
        return super().form_valid(form)


class DepositDetailView(DetailView):
    model = Deposit
    template_name = "deposits/deposit_detail.html"  # adjust path if needed
    context_object_name = "deposit"


class RentPaymentDetailView(DetailView):
    model = RentPayment
    template_name = "rent_payments/rent_payment_detail.html"  # adjust path if needed
    context_object_name = "rent_payment"


def create_lease_and_landlord(request):
    if request.method == "POST":
        lease_form = LeaseApplicationForm(request.POST)
        #        landlord_form = LandLordForm(request.POST, request.FILES)

        # Get employee numbers from POST
        primary_employee_number = request.POST.get("primary-employee_number")
        joint_employee_number = request.POST.get("joint-employee_number")
        landlord_code = request.POST.get("landlord_code")
        # Try to find existing employees
        primary_employee_instance = Employee.objects.filter(
            employee_number=primary_employee_number
        ).first()

        joint_employee_instance = None
        if joint_employee_number:
            joint_employee_instance = Employee.objects.filter(
                employee_number=joint_employee_number
            ).first()
        landlord_instance = LandLord.objects.filter(landlord_code=landlord_code).first()
        # If found, pass instance to the form → form treats it as update
        primary_employee_form = EmployeeForm(
            request.POST, prefix="primary", instance=primary_employee_instance
        )
        joint_employee_form = EmployeeForm(
            request.POST, prefix="joint", instance=joint_employee_instance
        )
        landlord_form = LandLordForm(
            request.POST, request.FILES, instance=landlord_instance
        )
        if (
            lease_form.is_valid()
            and landlord_form.is_valid()
            and primary_employee_form.is_valid()
        ):
            if (
                lease_form.cleaned_data["type_of_lease"] == "joint"
                and not joint_employee_form.is_valid()
            ):
                pass  # show form with errors
            else:
                primary_employee = primary_employee_form.save(commit=False)
                if not primary_employee.pk:
                    primary_employee.created_by = request.user
                primary_employee.updated_by = request.user
                primary_employee.save()
                joint_employee = None
                if lease_form.cleaned_data["type_of_lease"] == "joint":
                    joint_employee = joint_employee_form.save(commit=False)
                    if not joint_employee.pk:
                        joint_employee.created_by = request.user
                    joint_employee.updated_by = request.user
                    joint_employee.save()
                lease = lease_form.save(commit=False)
                lease.primary_employee = primary_employee
                lease.joint_employee = joint_employee

                landlord = landlord_form.save(commit=False)

                if not landlord.pk:
                    landlord.created_by = request.user
                landlord.updated_by = request.user

                landlord.save()

                lease.landlord = landlord
                lease.created_by = request.user
                lease.updated_by = request.user
                lease.save()
                # lease.landlord = landlord
                # lease.save()

                return redirect(lease.get_absolute_url())

    else:
        lease_form = LeaseApplicationForm()
        primary_employee_form = EmployeeForm(prefix="primary")
        joint_employee_form = EmployeeForm(prefix="joint")
        landlord_form = LandLordForm()

    return render(
        request,
        "lease_application/lease_application_form.html",
        {
            "lease_form": lease_form,
            "landlord_form": landlord_form,
            "primary_employee_form": primary_employee_form,
            "joint_employee_form": joint_employee_form,
            "title": "New Lease Application",
        },
    )


def edit_lease_and_landlord(request, pk):
    lease = get_object_or_404(LeaseApplication, pk=pk)
    # landlord = get_object_or_404(LandLord, lease=lease)
    landlord = lease.landlord
    # If you ever allow NULL primary/joint employee, use get_object_or_404 with fallback
    primary_employee = lease.primary_employee
    joint_employee = lease.joint_employee  # May be None

    if request.method == "POST":
        lease_form = LeaseApplicationForm(request.POST, instance=lease)
        # primary_employee_form = EmployeeForm(
        #     request.POST, prefix="primary", instance=primary_employee
        # )
        # joint_employee_form = EmployeeForm(
        #     request.POST,
        #     prefix="joint",
        #     instance=joint_employee if joint_employee else None,
        # )
        # Get employee numbers from POST
        primary_employee_number = request.POST.get("primary-employee_number")
        joint_employee_number = request.POST.get("joint-employee_number")
        # landlord_code = request.POST.get("landlord_code")

        # Try to find existing employees
        primary_employee_instance = Employee.objects.filter(
            employee_number=primary_employee_number
        ).first()

        joint_employee_instance = None
        if joint_employee_number:
            joint_employee_instance = Employee.objects.filter(
                employee_number=joint_employee_number
            ).first()

        # If found, pass instance to the form → form treats it as update
        primary_employee_form = EmployeeForm(
            request.POST, prefix="primary", instance=primary_employee_instance
        )
        joint_employee_form = EmployeeForm(
            request.POST, prefix="joint", instance=joint_employee_instance
        )
        landlord_code = request.POST.get("landlord_code")
        if landlord_code:
            landlord = LandLord.objects.filter(landlord_code=landlord_code).first()
            landlord_form = LandLordForm(request.POST, request.FILES, instance=landlord)
        else:
            landlord = lease.landlord  # LandLord.objects.get(lease=lease)
            landlord_form = LandLordForm(
                request.POST, request.FILES, instance=landlord
            )  # , instance=landlord)
        if (
            lease_form.is_valid()
            and landlord_form.is_valid()
            and primary_employee_form.is_valid()
        ):
            if (
                lease_form.cleaned_data["type_of_lease"] == "joint"
                and not joint_employee_form.is_valid()
            ):
                pass  # Fall through and re-render with errors
            else:
                primary_employee = primary_employee_form.save(commit=False)
                if not primary_employee.pk:
                    primary_employee.created_by = request.user
                primary_employee.updated_by = request.user
                primary_employee.save()
                joint_employee_instance = None
                if lease_form.cleaned_data["type_of_lease"] == "joint":
                    joint_employee_instance = joint_employee_form.save(commit=False)
                    if not joint_employee_instance.pk:
                        joint_employee_instance.created_by = request.user
                    joint_employee_instance.updated_by = request.user
                    joint_employee_instance.save()
                else:
                    # If the lease was previously joint but now changed:
                    lease.joint_employee = None
                    if joint_employee:
                        joint_employee.delete()  # Or keep, if you want to preserve them!

                lease = lease_form.save(commit=False)
                lease.primary_employee = primary_employee
                lease.joint_employee = joint_employee_instance

                landlord = landlord_form.save(commit=False)
                if not landlord.pk:
                    landlord.created_by = request.user
                landlord.updated_by = request.user

                lease.landlord = landlord
                # landlord.lease = lease
                landlord.save()
                lease.updated_by = request.user
                lease.save()
                return redirect(lease.get_absolute_url())

    else:
        lease_form = LeaseApplicationForm(instance=lease)
        primary_employee_form = EmployeeForm(
            prefix="primary", instance=primary_employee
        )
        joint_employee_form = EmployeeForm(prefix="joint", instance=joint_employee)
        landlord_form = LandLordForm(instance=landlord)

    return render(
        request,
        "lease_application/lease_application_form.html",
        {
            "lease_form": lease_form,
            "primary_employee_form": primary_employee_form,
            "joint_employee_form": joint_employee_form,
            "landlord_form": landlord_form,
            "title": "Edit Lease Application",
        },
    )


def lease_detail(request, pk):
    lease = get_object_or_404(
        LeaseApplication.objects.select_related(
            "primary_employee",
            "joint_employee",
            "landlord",
        ),
        pk=pk,
    )  #

    rent_payments = (
        RentPayment.objects.select_related("lease")
        .filter(lease=lease)
        .order_by("rent_start_date")
    )
    deposit = Deposit.objects.filter(lease=lease).first()
    form = RentPaymentPaidForm()
    return render(
        request,
        "lease_application/lease_application_detail.html",
        {
            "lease": lease,
            "rent_payments": rent_payments,
            "deposit": deposit,
            "form": form,
        },
    )


class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object

        # Get all leases where this employee is primary or joint
        leases = LeaseApplication.objects.filter(
            Q(primary_employee=employee) | Q(joint_employee=employee)
        )

        context["leases"] = leases
        return context


class LandlordDetailView(DetailView):
    model = LandLord
    template_name = "landlords/landlord_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        landlord = self.object

        # Get all leases where this landlord is involved
        leases = LeaseApplication.objects.filter(landlord=landlord)

        context["leases"] = leases
        return context


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = LeaseApplication
    form_class = LeaseApplicationForm
    template_name = "lease_application/lease_application_form.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # Only update this
        return super().form_valid(form)


class ApplicationListView(LoginRequiredMixin, SingleTableView):
    model = LeaseApplication
    table_class = LeaseApplicationTable
    template_name = "lease_application/lease_application_list.html"

    def get_queryset(self):
        return (
            LeaseApplication.objects.select_related(
                "primary_employee", "joint_employee", "landlord"
            )
            # .filter(status="pending")
            .order_by("lease_start_date")
        )


class ApplicationActiveListView(SingleTableView):
    model = LeaseApplication
    table_class = LeaseApplicationTable
    template_name = "lease_application/lease_application_list.html"

    def get_queryset(self):
        today = timezone.now().date()
        return (
            LeaseApplication.objects.select_related(
                "primary_employee", "joint_employee", "landlord"
            )
            .filter(lease_end_date__gte=today)
            .order_by("lease_end_date")
        )


class ApplicationExpiredListView(SingleTableView):
    model = LeaseApplication
    table_class = LeaseApplicationTable
    template_name = "lease_application/lease_application_list.html"

    def get_queryset(self):
        today = timezone.now().date()
        return (
            LeaseApplication.objects.select_related(
                "primary_employee", "joint_employee", "landlord"
            )
            .filter(lease_end_date__lt=today)
            .order_by("lease_end_date")
        )


class EmployeeListView(SingleTableView):
    model = Employee
    table_class = EmployeeTable
    template_name = "employees/employee_list.html"


class LandlordListView(SingleTableView):
    model = LandLord
    table_class = LandlordTable
    template_name = "landlords/landlord_list.html"


class RentPaymentFilteredTableView(SingleTableView):
    model = RentPayment
    table_class = RentPaymentTable
    template_name = "rent_payments/rent_payment_list.html"
    paginate_by = 1000  # Optional, for pagination

    def get_queryset(self):
        lease_type = self.kwargs.get(
            "lease_type"
        )  # company_lease / personal_lease / None
        status = self.kwargs.get("status")  # pending / paid / failed / None
        print(lease_type, status)

        qs = RentPayment.objects.select_related("lease")

        # Lease type filtering
        if lease_type == "company":
            qs = qs.filter(lease__type_of_lease__in=["company", "joint"])
        elif lease_type == "personal":
            qs = qs.filter(lease__type_of_lease="personal")

        # Status filtering
        if status in ["pending", "paid", "failed"]:
            qs = qs.filter(status=status)

        # Sorting
        if status == "pending" or status is None:
            qs = qs.order_by("rent_start_date")
        else:
            qs = qs.order_by("-date_of_payment")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RentPaymentPaidForm()
        context["lease_type"] = self.kwargs.get("lease_type")
        context["status"] = self.kwargs.get("status")
        return context


class DepositListView(SingleTableView):
    model = Deposit
    table_class = DepositTable
    template_name = "deposits/deposit_list.html"

    def get_queryset(self):
        return (
            Deposit.objects.select_related(
                "lease", "lease__primary_employee", "lease__landlord"
            )  # , "employee", "landlord")
            # .filter(status="pending")
            # .order_by("rent_start_date")
        )


def deposit_list(request):
    today = timezone.now().date()

    queryset = Deposit.objects.select_related(
        "lease", "lease__primary_employee", "lease__landlord"
    ).filter(lease__lease_end_date__lt=today, current_status="paid")

    table = DepositTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render(request, "deposits/deposit_list.html", {"table": table})


def lease_list_without_deposit(request):
    today = timezone.now().date()

    queryset = LeaseApplication.objects.select_related(
        "primary_employee", "joint_employee", "landlord"
    ).filter(
        type_of_lease__in=["company", "joint"],
        lease_end_date__gte=today,
        deposit__isnull=True,
    )

    table = LeaseApplicationTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render(
        request, "lease_application/lease_application_list.html", {"table": table}
    )


def generate_rent_payments(request):
    today = timezone.now().date()
    end_of_prev_month = today.replace(day=1) - timedelta(days=1)
    start_of_prev_month = end_of_prev_month.replace(day=1)
    valid_leases = LeaseApplication.objects.filter(
        lease_start_date__lte=end_of_prev_month, lease_end_date__gte=start_of_prev_month
    )

    for lease in valid_leases:
        # Check if payment for this lease for this month exists
        first_of_month = end_of_prev_month.replace(day=1)
        lease_start_date = lease.lease_start_date
        lease_end_date = lease.lease_end_date

        rent_start_date, rent_end_date = get_rent_period(
            max(lease_start_date, first_of_month), lease_end_date
        )
        # print(rent_start_date)
        rent_amount = calculate_pro_rata_rent(lease, rent_start_date, rent_end_date)
        payment_exists = RentPayment.objects.filter(
            lease=lease,
            rent_start_date__year=first_of_month.year,
            rent_start_date__month=first_of_month.month,
        ).exists()

        if payment_exists:
            print(f"Payment already exists for lease {lease.pk}")
            continue

        if lease.type_of_lease in ["company", "joint"]:
            payee_type = "landlord"
            landlord = lease.landlord
            if not landlord:
                print(f"No landlord found for lease {lease.pk}")
                continue
            payee_name = landlord.landlord_name
            payee_account_number = landlord.bank_account_number
            payee_ifsc = landlord.bank_ifsc_code

        elif lease.type_of_lease == "personal":
            payee_type = "employee"
            employee = lease.primary_employee
            payee_name = employee.employee_name if employee else None
            payee_account_number = None
            payee_ifsc = None
            # payee_account_number = employee.bank_account_number  # If you store it!
            # payee_ifsc = employee.bank_ifsc_code

        else:
            print(f"Unknown lease type for lease {lease.pk}")
            continue

        payment = RentPayment(
            lease=lease,
            amount=rent_amount,
            rent_start_date=rent_start_date,
            rent_end_date=rent_end_date,  # Or last day of month
            date_of_payment=None,
            utr_number="",  # Fill later when paid
            remarks="Auto-generated rent payment",
            #  created_by="system",
            # updated_by="system",
            payee_name=payee_name,
            payee_account_number=payee_account_number,
            payee_ifsc=payee_ifsc,
            payee_type=payee_type,
        )
        payment.save()
        print(f"Created rent payment for lease {lease.pk} → {payee_name}")
    return HttpResponse("Rent payments generated")


def get_rent_period(start_date, lease_end_date):
    """
    start_date: any date in the month you're generating for
    lease_end_date: Lease's actual end date

    Returns: tuple (rent_start_date, rent_end_date)
    """
    year = start_date.year
    month = start_date.month

    # 1st of the month
    #    rent_start_date = start_date.replace(day=1)
    # rent_start_date = start_date
    # Last day of this month
    last_day_of_month = calendar.monthrange(year, month)[1]
    month_end_date = date(year, month, last_day_of_month)

    # rent_end_date is whichever is earlier
    rent_end_date = min(month_end_date, lease_end_date)

    return start_date, rent_end_date


def calculate_pro_rata_rent(lease, period_start, period_end):
    """
    lease: your LeaseApplication instance
    period_start: rent_start_date for this payment (1st of month)
    period_end: rent_end_date for this payment (min(lease_end_date, last day of month))
    """
    # Total days in the rent period
    total_days_in_month = calendar.monthrange(period_start.year, period_start.month)[1]
    days_covered = (period_end - period_start).days + 1  # inclusive

    # Calculate proportion
    proportionate_rent = lease.rent * (days_covered / total_days_in_month)
    return round(proportionate_rent, 2)


def renew_lease(request, pk):
    old_lease = get_object_or_404(LeaseApplication, pk=pk)
    # landlord = get_object_or_404(LandLord, lease=old_lease)
    # landlord = old_lease.landlord
    if request.method == "POST":
        lease_form = LeaseApplicationForm(request.POST)
        # primary_employee_form = EmployeeForm(request.POST, prefix="primary")
        # joint_employee_form = EmployeeForm(request.POST, prefix="joint")
        # landlord_form = LandLordForm(request.POST, request.FILES)

        if lease_form.is_valid():
            #     and landlord_form.is_valid()
            #     and primary_employee_form.is_valid()
            # ):
            # if (
            #     lease_form.cleaned_data["type_of_lease"] == "joint"
            #     and not joint_employee_form.is_valid()
            # ):
            #     # Joint selected, but second form invalid
            #     pass
            # else:
            #     primary_employee = primary_employee_form.save()
            #     joint_employee = None
            #     if lease_form.cleaned_data["type_of_lease"] == "joint":
            #         joint_employee = joint_employee_form.save()

            lease = lease_form.save(commit=False)
            lease.primary_employee = old_lease.primary_employee
            lease.joint_employee = old_lease.joint_employee
            lease.landlord = old_lease.landlord

            # Force new lease start date to +1 day of old end date
            #            lease.lease_start_date = old_lease.lease_end_date + timedelta(days=1)

            lease.save()

            # landlord = landlord_form.save(commit=False)
            # landlord.lease = lease
            # landlord.save()

            return redirect(lease.get_absolute_url())

    else:
        # Pre-fill: type_of_lease, rent, deposit, employees
        lease_form = LeaseApplicationForm(
            initial={
                "type_of_lease": old_lease.type_of_lease,
                "lease_start_date": old_lease.lease_end_date + timedelta(days=1),
                "lease_deposit": old_lease.lease_deposit,
                "rent": old_lease.rent,
                "remarks": old_lease.remarks,
            }
        )

    return render(
        request,
        "lease_application/lease_application_renewal_form.html",
        {
            "lease_form": lease_form,
            "old_lease": old_lease,
        },
    )


def get_employee_by_number(request):
    employee_number = request.GET.get("employee_number")

    try:
        employee = Employee.objects.get(employee_number=employee_number)
    except Employee.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    data = model_to_dict(
        employee,
        fields=[
            "employee_number",
            "employee_name",
            "employee_mobile_number",
            "employee_designation",
            "office_code",
            "department",
            "office_name",
            "housing_loan",
            "housing_loan_location",
        ],
    )
    return JsonResponse(data)


def get_landlord_by_code(request):
    landlord_code = request.GET.get("landlord_code")
    landlord = LandLord.objects.get(landlord_code=landlord_code)
    landlord_form = LandLordForm(instance=landlord)
    return render(
        request,
        "landlords/_landlord_form_partial.html",
        {"landlord_form": landlord_form},
    )


def generate_rent_payments_for_lease(request, pk):
    lease = get_object_or_404(LeaseApplication, pk=pk)

    today = timezone.now().date()
    end_of_prev_month = today.replace(day=1) - timedelta(days=1)

    lease_end = min(lease.lease_end_date, end_of_prev_month)

    current_month = lease.lease_start_date
    created_count = 0

    while current_month <= lease_end:
        rent_start_date, rent_end_date = get_rent_period(
            current_month, lease.lease_end_date
        )

        # Check if payment already exists
        payment_exists = RentPayment.objects.filter(
            lease=lease, rent_start_date=rent_start_date, rent_end_date=rent_end_date
        ).exists()

        if payment_exists:
            current_month = current_month.replace(day=1) + relativedelta(months=1)
            continue

        rent_amount = calculate_pro_rata_rent(lease, rent_start_date, rent_end_date)

        if lease.type_of_lease in ["company", "joint"]:
            payee_type = "landlord"
            landlord = lease.landlord
            if not landlord:
                print(f"No landlord found for lease {lease.pk}")
                current_month = current_month.replace(day=1) + relativedelta(months=1)
                continue
            payee_name = landlord.landlord_name
            payee_account_number = landlord.bank_account_number
            payee_ifsc = landlord.bank_ifsc_code

        elif lease.type_of_lease == "personal":
            payee_type = "employee"
            employee = lease.primary_employee
            if not employee:
                print(f"No employee found for lease {lease.pk}")
                current_month = current_month.replace(day=1) + relativedelta(months=1)
                continue
            payee_name = employee.employee_name
            payee_account_number = None
            payee_ifsc = None

        else:
            print(f"Unknown lease type for lease {lease.pk}")
            current_month = current_month.replace(day=1) + relativedelta(months=1)
            continue

        RentPayment.objects.create(
            lease=lease,
            amount=rent_amount,
            rent_start_date=rent_start_date,
            rent_end_date=rent_end_date,
            date_of_payment=None,
            utr_number="",
            remarks="Auto-generated rent payment",
            created_by=request.user,
            updated_by=request.user,
            payee_name=payee_name,
            payee_account_number=payee_account_number,
            payee_ifsc=payee_ifsc,
            payee_type=payee_type,
        )
        created_count += 1
        print(f"Created rent payment for lease {lease.pk} → {payee_name}")

        current_month = current_month.replace(day=1) + relativedelta(months=1)

    return redirect(lease.get_absolute_url())


@require_POST
def mark_rent_payment_paid(request, pk):
    payment = get_object_or_404(RentPayment, pk=pk)
    form = RentPaymentPaidForm(request.POST)

    if form.is_valid():
        payment.date_of_payment = form.cleaned_data["date_of_payment"]
        payment.utr_number = form.cleaned_data["utr_number"]
        payment.remarks = form.cleaned_data["remarks"]
        payment.status = "paid"
        payment.updated_by = request.user  # Or request.user if ForeignKey
        payment.save()
        messages.success(
            request, f"Rent payment for {payment.rent_start_date} marked as paid."
        )
    else:
        messages.error(request, "Invalid data submitted.")

    return redirect(payment.lease.get_absolute_url())


@require_POST
def rent_payment_bulk_mark_paid(request):
    payment_ids = request.POST.get("payment_ids", "")
    ids = [int(pk) for pk in payment_ids.split(",") if pk.isdigit()]

    date_of_payment = request.POST.get("date_of_payment")
    utr_number = request.POST.get("utr_number", "")
    remarks = request.POST.get("remarks", "")

    updated_count = RentPayment.objects.filter(pk__in=ids, status="pending").update(
        status="paid",
        date_of_payment=date_of_payment,
        utr_number=utr_number,
        remarks=remarks,
        updated_by=request.user,  # or request.user if using FK
    )

    messages.success(request, f"{updated_count} payments marked as paid.")
    return redirect("rent_list")  # update as needed
