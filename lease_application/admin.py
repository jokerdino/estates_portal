from django.contrib import admin

# Register your models here.
from .models import (
    LeaseApplication,
    LandLord,
    RentPayment,
    Deposit,
    Eligibility,
    Employee,
)

# admin.site.register(LeaseApplication)
admin.site.register(LandLord)
admin.site.register(RentPayment)
admin.site.register(Deposit)
admin.site.register(Eligibility)
admin.site.register(Employee)


class LeaseApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "type_of_lease",
        "primary_employee",
        "joint_employee",
        "landlord",
        "lease_start_date",
        "lease_end_date",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "primary_employee",
            "joint_employee",
            "landlord",
        )


admin.site.register(LeaseApplication, LeaseApplicationAdmin)
