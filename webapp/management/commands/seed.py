import os

from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from webapp.models import Allocation, Request, Offer, ShipmentVentilator, Shipment, Ventilator, VentilatorModel, SystemParameters, System, HospitalGroup, Hospital, Supplier, User, UserRole
from webapp.views import create_shipment, run_algorithm
from webapp.serializers import VentilatorUpdateSerializer, ShipmentSerializer

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
                "username": "elmhurst_hospital_admin",
                "name": "Elmhurst Hospital Center",
                "address": "79-01 Broadway, Elmhurst, NY 11373"
            },
            {
                "username": "flushing_hospital_admin",
                "name": "Flushing Hospital Medical Center",
                "address": "45th Avenue & Parsons Blvd, Flushing, NY 11355"
            },
            {
                "username": "jamaica_hospital_admin",
                "name": "Jamaica Hospital Medical Center",
                "address": "89th Avenue & Van Wyck Expressway, Jamaica, NY 11418"
            },
            {
                "username": "lewis_hospital_admin",
                "name": "Lewis County General Hospital",
                "address": "3926 NY-12, Lyons Falls, NY 13368"
            },
            {
                "username": "brookdale_hospital_admin",
                "name": "Brookdale Hospital Medical Center",
                "address": "1 Brookdale Plaza, Brooklyn, NY 11212"
            },
            {
                "username": "general_hospital_admin",
                "name": "General Hospital",
                "address": "16 Bank St, Batavia, NY 14020"
            },
            {
                "username": "margaretville_hospital_admin",
                "name": "Margaretville Hospital",
                "address": "42084 NY-28, Margaretville, NY 12455"
            },
            {
                "username": "central_hospital_admin",
                "name": "Central New York Psychiatric Center",
                "address": "9005 Old River Rd, Marcy, NY 13403"
            },
            {
                "username": "nye_hospital_admin",
                "name": "New York Eye and Ear Infirmary of Mount Sinai",
                "address": "310 East 14th Street, New York, NY 10003"
            },
            {
                "username": "nyc_hospital_admin",
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
                username=hospital_addresses[user_count]['username']
            )
            user.set_password(default_pw)
            user.save()
        sys_admin_user = User(
            email="test11@gmail.com",
            username="sys_admin"
        )
        sys_admin_user.save()
        hospital_group_user = User(
            email="test12@gmail.com",
            username="hospital_ceo"
        )
        hospital_group_user.save()
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

        total_vent_count = 75
        first_vent_model_pk = VentilatorModel.objects.first().id
        first_hospital_model_pk = Hospital.objects.first().id

        for vent_count in range(total_vent_count):
            status = Ventilator.Status.Unavailable.name
            unavailable_code = Ventilator.UnavailableCode.PendingOffer.name
            if vent_count % 10 == 0:
                status = Ventilator.Status.SourceReserve.name
                unknown_status = None
            hosp = Hospital.objects.all()[vent_count % 4]
            vent_model = VentilatorModel.objects.get(pk=first_vent_model_pk + (vent_count % len(model_nums)))
            vent = Ventilator(
                ventilator_model=VentilatorModel.objects.get(pk=first_vent_model_pk + (vent_count % len(model_nums))),
                status=status,
                unavailable_code=unavailable_code,
                serial_number=str(vent_count),
                owning_hospital=hosp,
                current_hospital=hosp,
                monetary_value=vent_model.monetary_value,
                inserted_by_user=User.objects.first(),
                updated_by_user=User.objects.first()
            )
            vent.save()
        for hospital_count in range(10):
            h = Hospital.objects.all()[hospital_count]
            if hospital_count < 5:
                o = Offer(
                    status=Offer.Status.PendingApproval.name,
                    hospital=h,
                    offered_qty=Ventilator.objects.filter(is_valid=True).filter(status=Ventilator.Status.Unavailable.name).filter(unavailable_code=Ventilator.UnavailableCode.PendingOffer.name).filter(current_hospital=h).count(),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                if h.name == "Elmhurst Hospital Center":
                    o.status = Offer.Status.Approved.name
                    ventilators = Ventilator.objects.filter(is_valid=True).filter(current_hospital=h).filter(status=Ventilator.Status.Unavailable.name).filter(unavailable_code=Ventilator.UnavailableCode.PendingOffer.name)
                    for vent in ventilators:
                        vent.status = Ventilator.Status.Available.name
                        vent.unavailable_code = None
                        vent.save()
                o.save()
            else:
                r1 = Request(
                    status=Request.Status.PendingApproval.name,
                    hospital=h,
                    requested_qty=random.randint(5, 10),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                r2 = Request(
                    status=Request.Status.PendingApproval.name,
                    hospital=h,
                    requested_qty=random.randint(5, 10),
                    opened_by_user=user,
                    opened_at=datetime.now(),
                    inserted_by_user=User.objects.first(),
                    updated_by_user=User.objects.first()
                )
                if h.name == "General Hospital":
                    r1.status = Request.Status.Approved.name
                    r2.status = Request.Status.Approved.name
                r1.save()
                r2.save()
        user = User(
            email="admin_test@gmail.com".format(user_count),
            username="admin_user".format(user_count)
        )
        user.set_password(default_pw)
        user.save()
 
        UserRole.objects.create(
            user_role=UserRole.Role.NoRole.name,
            assigned_user=hospital_group_user,
            hospital_group=hospital_group,
            granted_by_user=user,
            inserted_by_user=user,
            updated_by_user=user
        )
        UserRole.objects.create(
            user_role=UserRole.Role.NoRole.name,
            assigned_user=sys_admin_user,
            system=sys,
            granted_by_user=user,
            inserted_by_user=user,
            updated_by_user=user
        )
        
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
        run_algorithm(user)
        alloc = Allocation.objects.first()
        ventilator_ids = []
        for ventilator in Ventilator.objects.filter(is_valid=True).filter(current_hospital=alloc.offer.hospital).filter(status=Ventilator.Status.Available.name)[:alloc.allocated_qty]:
            ventilator_ids.append(ventilator.id)
        create_shipment(alloc.id, alloc.allocated_qty, ventilator_ids, user)
        shipment = Shipment.objects.first()
        
        data = {}
        data['status'] = Shipment.Status.Shipped.name
        data['tracking_number'] = '123123'
        data['shipping_service'] = 'FedEx'
        serializer = ShipmentSerializer(shipment, data=data)
        if serializer.is_valid():
            serializer.save()
        data = {}
        data['status'] = Shipment.Status.Arrived.name
        serializer = ShipmentSerializer(shipment, data=data)
        if serializer.is_valid():
            serializer.save()
        ventilators = [shipment_ventilator.ventilator for shipment_ventilator in shipment.shipmentventilator_set.all()]
        for vent in ventilators:
            data['quality'] = vent.quality
            data['serial_number'] = vent.serial_number
            data['ventilator_model'] = {}
            data['ventilator_model']['manufacturer'] = vent.ventilator_model.manufacturer
            data['ventilator_model']['model'] = vent.ventilator_model.model
            data['ventilator_model']['monetary_value'] = vent.ventilator_model.monetary_value
            data['arrived_code'] = Ventilator.ArrivedCode.PassInspection.name
            data['unavailable_code'] = None
            data['status'] = Ventilator.Status.Arrived.name
            serializer = VentilatorUpdateSerializer(vent, data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)


