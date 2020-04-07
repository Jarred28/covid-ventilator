from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from webapp.models import Hospital, HospitalGroup, Order, User, Ventilator, SystemOperator, SystemParameters
import random
class Command(BaseCommand):
    help = "Seed the Database"
    hospital_addresses = [
        "777 Brockton Avenue, Abington MA 2351",
        "30 Memorial Drive, Avon MA 2322",
        "3222 State Rt 11, Malone NY 12953",
        "750 Academy Drive, Bessemer AL 35022",
        "625 School Street, Putnam CT 6260",
        "548 Market St, San Francisco, CA 94104-5401",
        "1313 Disneyland Dr, Anaheim, CA 92802",
        "214 S Wabash Ave, Chicago, IL 60604",
        "4211 Spicewood Springs Rd, Austin, TX 78759",
        "1375 Buena Vista Dr, Lake Buena Vista, FL 32830"
    ]

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
        for group_count in range(6):
            email = "{0}{1}{2}".format("covid_test_group", str(group_count), "@gmail.com")
            username = "{0}{1}".format("test_group", str(group_count))
            hg_user = User(
                user_type=User.UserType.HospitalGroup.name,
                email=email,
                username=username
            )
            hg_user.save()
            name = "{0}{1}".format("HospitalGroup", str(group_count))
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
            hg = HospitalGroup.objects.all()[pos]
            h = Hospital(
                name=name,
                user=h_user,
                address=self.hospital_addresses[hospital_count], 
                contribution=0, 
                projected_load=0, 
                hospital_group=hg, 
                within_group_only=False
            )
            h.save()
        for vent_count in range(100):
            hosp = Hospital.objects.all()[vent_count % 4]
            model = "{0}{1}".format("model", str(vent_count))
            vent = Ventilator(
                model_num=model,
                state=Ventilator.State.Available.name,
                owning_hospital=hosp,
                current_hospital=hosp
            )
            vent.save()
        for order_count in range(6):
            order = Order(
                num_requested=random.randint(20, 400),
                time_submitted=datetime.now(),
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
