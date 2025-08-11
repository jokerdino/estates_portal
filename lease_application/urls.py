from django.urls import path
from django.views.generic import RedirectView
from .views import (
    # index,
    # ApplicationCreateView,
    # ApplicationUpdateView,
    ApplicationListView,
    # ApplicationDetailView,
    create_lease_and_landlord,
    edit_lease_and_landlord,
    lease_detail,
    generate_rent_payments,
    # RentListView,
    RentPaymentFilteredTableView,
    DepositCreateView,
    # DepositRefundCreateView,
    DepositUpdateView,
    # DepositRefundUpdateView,
    DepositDetailView,
    DepositListView,
    renew_lease,
    get_employee_by_number,
    deposit_list,
    lease_list_without_deposit,
    LandlordListView,
    LandlordUpdateView,
    LandlordDetailView,
    LandlordCreateView,
    EmployeeListView,
    EmployeeUpdateView,
    EmployeeDetailView,
    EmployeeCreateView,
    generate_rent_payments_for_lease,
    mark_rent_payment_paid,
    rent_payment_bulk_mark_paid,
    RentPaymentDetailView,
    ApplicationExpiredListView,
    get_landlord_by_code,
)

urlpatterns = [
    path("", RedirectView.as_view(url="applications/", permanent=False)),
    path(
        "applications/expired",
        ApplicationExpiredListView.as_view(),
        name="lease_list_expired",
    ),
    path("applications/add/", create_lease_and_landlord, name="lease_add"),
    path(
        "applications/<int:pk>/",
        lease_detail,
        name="lease_detail",
    ),
    path(
        "applications/<int:pk>/edit",
        edit_lease_and_landlord,
        name="lease_edit",
    ),
    path("applications/", ApplicationListView.as_view(), name="lease_list"),
    path(
        "applications/no-deposit",
        lease_list_without_deposit,
        name="no_deposit_lease_list",
    ),
    path("applications/<int:pk>/renew/", renew_lease, name="lease_renew"),
    path(
        "lease/<int:pk>/generate-rent-payments/",
        generate_rent_payments_for_lease,
        name="generate_rent_payments_for_lease",
    ),
    path("generate_rent/", generate_rent_payments, name="generate_rent"),
    # path("rent/", RentListView.as_view(), name="rent_list"),
    path("rent/<int:pk>", RentPaymentDetailView.as_view(), name="rent_payment_detail"),
    path(
        "rent-payment/<int:pk>/mark-paid/",
        mark_rent_payment_paid,
        name="rent_payment_mark_paid",
    ),
    path(
        "rent-payments/bulk-mark-paid/",
        rent_payment_bulk_mark_paid,
        name="rent_payment_bulk_mark_paid",
    ),
    path("deposits/add/", DepositCreateView.as_view(), name="deposit_create"),
    path("deposits/<int:pk>/edit/", DepositUpdateView.as_view(), name="deposit_update"),
    path("deposits/<int:pk>/", DepositDetailView.as_view(), name="deposit_detail"),
    path("deposits/", DepositListView.as_view(), name="deposit_list"),
    path("deposits/expired", deposit_list, name="deposit_list_expired"),
    path("api/get-employee/", get_employee_by_number, name="get_employee"),
    path("api/get-landlord/", get_landlord_by_code, name="get_landlord"),
    path(
        "employees/<int:pk>/edit/", EmployeeUpdateView.as_view(), name="employee_update"
    ),
    path("employees/<int:pk>/", EmployeeDetailView.as_view(), name="employee_detail"),
    path("employees/", EmployeeListView.as_view(), name="employee_list"),
    path("employees/add/", EmployeeCreateView.as_view(), name="employee_create"),
    path(
        "landlords/<int:pk>/edit/", LandlordUpdateView.as_view(), name="landlord_update"
    ),
    path("landlords/<int:pk>/", LandlordDetailView.as_view(), name="landlord_detail"),
    path("landlords/", LandlordListView.as_view(), name="landlord_list"),
    path("landlords/add/", LandlordCreateView.as_view(), name="landlord_create"),
]

urlpatterns += [
    #    All rent payments
    path(
        "rent-payment/",
        RentPaymentFilteredTableView.as_view(),
        name="rent_list",
    ),
    # Company lease
    path(
        "rent-payment/<str:lease_type>/",
        RentPaymentFilteredTableView.as_view(),
        name="rent_lease_type_list",
    ),
    path(
        "rent-payment/<str:lease_type>/<str:status>/",
        RentPaymentFilteredTableView.as_view(),
        name="rent_status_list",
    ),
]
