import os

from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from webapp.models import Allocation, Request, Offer, ShipmentVentilator, Shipment, Ventilator, VentilatorModel, SystemParameters, System, HospitalGroup, Hospital, Supplier, User, UserRole
import random
class Command(BaseCommand):
    help = "Seed the Database"
    def add_arguments(self, parser):
        parser.add_argument("--reset_db", type=int)

    def delete_existing_records(self):
        Allocation.objects.all().delete()
        Request.objects.all().delete()
        Offer.objects.all().delete()
        ShipmentVentilator.objects.all().delete()
        Shipment.objects.all().delete()
        Ventilator.objects.all().delete()
        VentilatorModel.objects.all().delete()
        SystemParameters.objects.all().delete()
        System.objects.all().delete()
        HospitalGroup.objects.all().delete()
        Supplier.objects.all().delete()
        Hospital.objects.all().delete()
        User.objects.all().delete()
        UserRole.objects.all().delete()


    def handle(self, *args, **options):
        if options["reset_db"] == 0:
            return
        self.delete_existing_records()
        hospital_addresses = [
            {
                "name": "Elmhurst Hospital Center",
                "address": "79-01 Broadway, Elmhurst, NY 11373"
            },
            {
                "name": "Flushing Hospital Medical Center",
                "address": "45th Avenue & Parsons Blvd, Flushing, NY 11355"
            },
            {
                "name": "Jamaica Hospital Medical Center",
                "address": "89th Avenue & Van Wyck Expressway, Jamaica, NY 11418"
            },
            {
                "name": "Lewis County General Hospital",
                "address": "3926 NY-12, Lyons Falls, NY 13368"
            },
            {
                "name": "Brookdale Hospital Medical Center",
                "address": "1 Brookdale Plaza, Brooklyn, NY 11212"
            },
            {
                "name": "General Hospital",
                "address": "16 Bank St, Batavia, NY 14020"
            },
            {
                "name": "Margaretville Hospital",
                "address": "42084 NY-28, Margaretville, NY 12455"
            },
            {
                "name": "Central New York Psychiatric Center",
                "address": "9005 Old River Rd, Marcy, NY 13403"
            },
            {
                "name": "New York Eye and Ear Infirmary of Mount Sinai",
                "address": "310 East 14th Street, New York, NY 10003"
            },
            {
                "name": "New York Community Hospital of Brooklyn, Inc",
                "address": "2525 Kings Highway, Brooklyn, NY 11229"
            }
        ]
        model_nums = ["Medtronic Portable",
            "Medtronic Non-Portable",
            "Phillips Portable",
            "Phillips Non-Portable",
            "Hamilton Portable",
            "Hamilton Non-Portable"
        ]
        default_pw = os.environ.get('DEFAULT_PW')
        for user_count in range(10):
            user = User(
                email="test{0}@gmail.com".format(user_count),
                username="user{0}".format(user_count)
            )
            user.set_password(default_pw)
            user.save()
        for model_num in model_nums:
            m_value = random.randint(10000, 30000)
            vent_model = VentilatorModel(
                manufacturer='Default Manufacturer',
                model=model_num,
                monetary_value=m_value,
                inserted_by_user=User.objects.first(),
                updated_by_user=User.objects.first()
            )
            vent_model.save()

        sys_params = SystemParameters(
            destination_reserve=10.0,
            strategic_reserve=10.0,
            inserted_by_user=User.objects.first(),
            updated_by_user=User.objects.first()
        )
        sys_params.save()
        sys = System(
            name='Sys Operator',
            inserted_by_user=User.objects.first(),
            updated_by_user=User.objects.first()
        )
        sys.save()
        hospital_group = HospitalGroup(
            name='NY State',
            inserted_by_user=User.objects.first(),
            updated_by_user=User.objects.first()
        )
        hospital_group.save()

        for hospital_count in range(10):
            h = Hospital(
                name=hospital_addresses[hospital_count]['name'],
                address=hospital_addresses[hospital_count]['address'],
                hospital_group=hospital_group,
                within_group_only=True,
                current_load=random.randint(10, 30),
                projected_load=random.randint(40, 70),
                inserted_by_user=User.objects.first(),
                updated_by_user=User.objects.first()
            )
            h.save()
            if hospital_count < 5:
                o = Offer(
                    status=Offer.Status.Open.name,
                    hospital=h,
                    offered_qty=random.randint(5, 15),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                o.save()
            else:
                r1 = Request(
                    status=Request.Status.Open.name,
                    hospital=h,
                    requested_qty=random.randint(5, 10),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                r1.save()
                r2 = Request(
                    status=Request.Status.Open.name,
                    hospital=h,
                    requested_qty=random.randint(5, 10),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                r2.save()
        total_vent_count = 75
        first_vent_model_pk = VentilatorModel.objects.first().id
        first_hospital_model_pk = Hospital.objects.first().id
        user = User(
            email="admin_test@gmail.com".format(user_count),
            username="admin_user".format(user_count)
        )
        user.set_password(default_pw)
        user.save()
        for vent_count in range(total_vent_count):
            status = Ventilator.Status.Available.name
            if vent_count % 10 == 0:
                status = Ventilator.Status.SourceReserve.name
            hosp = Hospital.objects.all()[vent_count % 4]
            vent_model = VentilatorModel.objects.get(pk=first_vent_model_pk + (vent_count % len(model_nums)))
            vent = Ventilator(
                ventilator_model=VentilatorModel.objects.get(pk=first_vent_model_pk + (vent_count % len(model_nums))),
                status=status,
                unavailable_status=None,
                serial_number=str(vent_count),
                owning_hospital=hosp,
                current_hospital=hosp,
                monetary_value=vent_model.monetary_value,
                inserted_by_user=User.objects.first(),
                updated_by_user=User.objects.first()
            )
            vent.save()

        for count in range(15):
            if count < 10:
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=User.objects.all()[count],
                    hospital=Hospital.objects.all()[count],
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
            if count < 3:
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=User.objects.all()[count],
                    hospital_group=hospital_group,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
            if count == 4 or count == 5:
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=User.objects.all()[count],
                    system=sys,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )