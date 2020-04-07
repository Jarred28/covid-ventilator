from datetime import date
from django.core.management.base import BaseCommand, CommandError
from webapp.models import Hospital, HospitalGroup, Order, User, Ventilator, SystemOperator, SystemParameters
import random
class Command(BaseCommand):
    help = "Seed the Database"
    def add_arguments(self, parser):
        parser.add_argument("--reset_db", type=int)

    def delete_existing_records(self):
        Order.objects.all().delete()
        Hospital.objects.all().delete()
        Ventilator.objects.all().delete()
        HospitalGroup.objects.all().delete()
        User.objects.all().delete()

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
        email = "covid_test_group"
        username = "ny_state"
        hg_user = User(
            user_type=User.UserType.HospitalGroup.name,
            email=email,
            username=username
        )
        hg_user.save()
        name = "NY State"
        hg = HospitalGroup(name=name, user=User.objects.get(pk=hg_user.id))
        hg.save()
        for hospital_count in range(10):
            email = "{0}{1}{2}".format("covid_test_hospital", str(hospital_count), "@gmail.com")
            username = "{0}{1}".format("test_hospital", str(hospital_count))
            h_user = User(
                user_type=User.UserType.Hospital.name,
                email=email,
                username=username
            )
            h_user.save()
            name = "{0}{1}".format("Hospital", str(hospital_count))
            pos = 5 if hospital_count > 5 else hospital_count
            case_load = random.randint(40, 100)
            h = Hospital(
                name=hospital_addresses[hospital_count]['name'],
                user=h_user,
                address=hospital_addresses[hospital_count]['address'], 
                contribution=0, 
                projected_load=case_load, 
                hospital_group=hg, 
                within_group_only=False
            )
            h.save()
        for vent_count in range(20):
            hosp = Hospital.objects.all()[vent_count % 4]
            monetary_value = 0
            if ((vent_count) % len(model_nums)) % 2 == 0:
                monetary_value = random.randint(5000, 20000)
            else:
                monetary_value = random.randint(15000, 30000)
            vent = Ventilator(
                model_num=model_nums[(vent_count) % len(model_nums)],
                state=Ventilator.State.Available.name,
                owning_hospital=hosp,
                current_hospital=hosp,
                monetary_value=monetary_value
            )
            vent.save()
        for order_count in range(6):
            num_req = random.randint(10, 30)
            order = Order(
                num_requested=random.randint(20, 400),
                time_submitted=date(2020, 4, 9),
                active=True,
                auto_generated=False,
                requesting_hospital=Hospital.objects.all()[order_count+4],
            )
            order.save()

        SystemParameters.getInstance().destination_reserve = 10.0
        SystemParameters.getInstance().strategic_reserve = 10.0
        SystemParameters.getInstance().save()
        sys_oper_user = User(
                user_type=User.UserType.SystemOperator.name,
                email="sys_admin_covid@gmail.com",
                username="sys_admin"
            )
        sys_oper_user.save()
        sys_oper = SystemOperator(
            name="admin",
            user=User.objects.get(pk=sys_oper_user.id)
        )
        sys_oper.save()
