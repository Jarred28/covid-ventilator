import csv
import io
from collections import defaultdict
from datetime import date
import pdb

from datetime import datetime
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status


from . import notifications
from webapp.algorithm import algorithm
from webapp.models import Hospital, HospitalGroup, Order, User, Ventilator, ShipmentBatches, SystemParameters, SystemOperator
from webapp.permissions import HospitalPermission, HospitalGroupPermission, SystemOperatorPermission
from webapp.serializers import SignupSerializer, SystemParametersSerializer, VentilatorSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request, format=None):
    if request.user.user_type == User.UserType.Hospital.name:
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))
    if request.user.user_type == User.UserType.SystemOperator.name:
        return HttpResponseRedirect(reverse('sys-dashboard', request=request, format=format))
    if request.user.user_type == User.UserType.HospitalGroup.name:
        return HttpResponseRedirect(reverse('ceo-dashboard', request=request, format=format))
    return Response(status=status.HTTP_204_NO_CONTENT)


class RequestCredentials(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registration/request_credentials.html'

    def get(self, request):
        serializer = SignupSerializer()
        return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})
        serializer.save()
        return HttpResponseRedirect(reverse('login', request=request))


class OrderInfo(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/order.html'

    # Gives all of your requested ventilators + ventilator orders you have out.
    def get(self, request, format=None):
        hospital = Hospital.objects.get(user=request.user)
        # Demand ventilators should also be segmented? 
        all_demand_ventilator_orders = list(Order.objects.filter(requesting_hospital=hospital))
        active_demand_orders = []
        reserve_demand_orders = []
        requested_reserve_demand_orders = []
        for order in all_demand_ventilator_orders:
            if order.active == True:
                active_demand_orders.append(order)
            if Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name).count() > 0:
                reserve_demand_orders.append(order)
            if Ventilator.objects.filter(order=order).filter(state=Ventilator.State.RequestedReserve.name).count() > 0:
                requested_reserve_demand_orders.append(order)
        all_sent_ventilator_orders = list(Order.objects.filter(sending_hospital=hospital))
        # ventilators = [[order.ventilator_set.all()] for order in all_sent_ventilator_orders]
        transit_orders = []
        arrived_reserve_orders = []
        arrived_non_reserve_orders = []
        arrived_requested_reserve_orders = []
        for sent_order in all_sent_ventilator_orders:
            # Replacing num_requested with actual amt shipped for copy of object for purposes of frontend.
            ventilators = sent_order.ventilator_set.all()
            if ventilators.count() == 0:
                continue
            sent_order.num_requested = ventilators.count()
            if (ventilators.first().state == Ventilator.State.InTransit.name):
                # No Manipulation on in-transit orders
                transit_orders.append(sent_order)
            else:
                # Ventilators are at the location.
                if (ventilators.filter(state=Ventilator.State.Reserve.name)):
                    # There are reserve ventilators.
                    arrived_reserve_orders.append(sent_order)
                elif (ventilators.filter(state=Ventilator.State.RequestedReserve.name)):
                    arrived_requested_reserve_orders.append(sent_order)
                else:
                    arrived_non_reserve_orders.append(sent_order)
        return Response({
                'active_demand_orders': active_demand_orders,
                'reserve_demand_orders': reserve_demand_orders,
                'requested_reserve_demand_orders': requested_reserve_demand_orders,
                'transit_orders': transit_orders,
                'arrived_reserve_orders': arrived_reserve_orders,
                'arrived_requested_reserve_orders': arrived_requested_reserve_orders,
                'arrived_non_reserve_orders': arrived_non_reserve_orders
        })

    def post(self, request, format=None):
        hospital = Hospital.objects.get(user=request.user)
        order = Order(
            num_requested=request.data['num_requested'],
            time_submitted=datetime.now(),
            active=True,
            auto_generated=False,
            requesting_hospital=hospital,
        )
        order.save()
        demand_ventilator_orders = list(Order.objects.filter(requesting_hospital=hospital))
        all_sent_ventilator_orders = list(Order.objects.filter(sending_hospital=hospital))
        transit_orders = []
        arrived_reserve_orders = []
        arrived_non_reserve_orders = []
        requested_reserve_orders = []
        for sent_order in all_sent_ventilator_orders:
            # Replacing num_requested with actual amt shipped for copy of object for purposes of frontend.
            ventilators = sent_order.ventilator_set.all()
            if ventilators.count() == 0:
                continue
            sent_order.num_requested = ventilators.count()

            if (ventilators.first().state == Ventilator.State.InTransit.name):
                # No Manipulation on in-transit orders
                transit_orders.append(sent_order)
            else:
                # Ventilators are at the location.
                if (ventilators.filter(state=Ventilator.State.Reserve.name)):
                    # There are reserve ventilators.
                    arrived_reserve_orders.append(sent_order)
                elif (ventilators.filter(state=Ventilator.State.RequestedReserve.name)):
                    requested_reserve_orders.append(sent_order)
                else:
                    arrived_non_reserve_orders.append(sent_order)
        return Response({
                'demand_orders': demand_ventilator_orders,
                'transit_orders': transit_orders,
                'arrived_reserve_orders': arrived_reserve_orders,
                'arrived_non_reserve_orders': arrived_non_reserve_orders,
                'requested_reserve_orders': requested_reserve_orders
        })


class VentilatorList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/dashboard.html'

    def get(self, request, format=None):
        ventilators = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user))

        # If any ventilators are InTransit, let the user know
        in_transit_ventilators = ventilators.filter(state=Ventilator.State.InTransit.name)
        if in_transit_ventilators:
            batchid_to_ventilators = defaultdict(list)
            for ventilator in in_transit_ventilators:
                batchid_to_ventilators[ventilator.batch_id].append(ventilator)
            for batchid, vents in batchid_to_ventilators.items():
                messages.add_message(request, messages.INFO, "%d ventilator(s) are in transit" % len(vents), str(batchid))

        serializer = VentilatorSerializer(Ventilator.objects.first())
        return Response({'ventilators': ventilators, 'serializer': serializer})

    def post(self, request, format=None):
        # Either batch upload through CSV  or add single ventilator entry
        csv_file = request.FILES.get('file', None)
        if csv_file:
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)

            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                ventilator = Ventilator(
                    model_num=column[0], state=column[1],
                    owning_hospital=Hospital.objects.get(user=request.user),
                    current_hospital=Hospital.objects.get(user=request.user)
                )
                ventilator.save()
        else:
            if not request.data.get("model_num", None) or not request.data.get("state", None):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            ventilator = Ventilator(
                model_num=request.data["model_num"], state=request.data["state"],
                owning_hospital=Hospital.objects.get(user=request.user),
                current_hospital=Hospital.objects.get(user=request.user)
            )
            ventilator.save()

        ventilators = Ventilator.objects.filter(owning_hospital=Hospital.objects.get(user=request.user))
        serializer = VentilatorSerializer(ventilator)
        return Response({'ventilators': ventilators, 'serializer': serializer})

@api_view(['POST'])
@permission_classes([IsAuthenticated&HospitalPermission])
def call_back_reserve(request, order_id, format=None):
    order = Order.objects.get(pk=order_id)
    requisitioned_ventilators = Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name)
    batch_id = ShipmentBatches.getInstance().max_batch_id
    batch_id += 1
    for ventilator in requisitioned_ventilators:
        ventilator.state = Ventilator.State.InTransit.name
        ventilator.current_hospital = order.sending_hospital
        ventilator.batch_id = batch_id
        ventilator.save()
        # Need to send notification to receiving hospital.
    notifications.send_requisitioned_email(order.sending_hospital, order.requesting_hospital, requisitioned_ventilators.count())
    ShipmentBatches.update(batch_id)
    return HttpResponseRedirect(reverse('order', request=request))

def change_ventilator_state(order_id, old_state, new_state):
    order = Order.objects.get(pk=order_id)
    allowed_ventilators = Ventilator.objects.filter(order=order).filter(state=old_state)
    for ventilator in allowed_ventilators:
        ventilator.state = new_state
        ventilator.save()
    return allowed_ventilators.count()

@api_view(['POST'])
@permission_classes([IsAuthenticated&HospitalPermission])
def deploy_reserve(request, order_id, format=None):
    count = change_ventilator_state(order_id, Ventilator.State.Reserve.name, Ventilator.State.Available.name)
    if count == 0:
        count = change_ventilator_state(order_id, Ventilator.State.RequestedReserve.name, Ventilator.State.Available.name)
    # Need to send emails to receiving hospital.
    order = Order.objects.get(pk=order_id)
    notifications.send_deployable_email(order.sending_hospital, order.requesting_hospital, count)
    return HttpResponseRedirect(reverse('order', request=request))

@api_view(['POST'])
@permission_classes([IsAuthenticated&HospitalPermission])
def request_reserve(request, order_id, format=None):
    count = change_ventilator_state(order_id, Ventilator.State.Reserve.name, Ventilator.State.RequestedReserve.name)
    order = Order.objects.get(pk=order_id)
    notifications.send_requested_reserve_email(order.sending_hospital, order.requesting_hospital, count)
    return HttpResponseRedirect(reverse('order', request=request))

@api_view(['POST'])
@permission_classes([IsAuthenticated&HospitalPermission])
def deny_reserve(request, order_id, format=None):
    count = change_ventilator_state(order_id, Ventilator.State.RequestedReserve.name, Ventilator.State.Reserve.name)
    order = Order.objects.get(pk=order_id)
    notifications.send_denied_reserve_email(order.sending_hospital, order.requesting_hospital, count)
    return HttpResponseRedirect(reverse('order', request=request))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes([HospitalPermission|HospitalGroupPermission])
def approve_ventilators(request, batchid, format=None):
    ventilators = Ventilator.objects.filter(batch_id=batchid)
    # TODO(hacky): HospitalGroup and Hospital should not be using the same endpoint
    # when they're using it for different functionalities
    if request.user.user_type == User.UserType.Hospital.name:
        reserve_amt = 0
        # This means it wasn't a requisition
        if not ventilators.first().order.sending_hospital == Hospital.objects.get(user=request.user):
            reserve_amt = SystemParameters.getInstance().destination_reserve / 100  * len(ventilators)
        reserve_ventilator_count = 0
        for vent in ventilators:
            if vent.state == Ventilator.State.InTransit.name:
                if reserve_ventilator_count < reserve_amt:
                    vent.state = Ventilator.State.Reserve.name
                    reserve_ventilator_count += 1
                else:
                    vent.state = Ventilator.State.Available.name
            vent.save()
    elif request.user.user_type == User.UserType.HospitalGroup.name:
        for vent in ventilators:
            if vent.state == Ventilator.State.Requested.name:
                vent.state = Ventilator.State.InTransit.name
                vent.current_hospital = vent.order.requesting_hospital
            vent.save()
        order = ventilators[0].order
        order.date_fulfilled = datetime.now()
        order.save()
    return HttpResponseRedirect(reverse('home', request=request, format=format))    


class VentilatorDetail(APIView):
    serializer_class = VentilatorSerializer
    permission_classes = [IsAuthenticated&HospitalPermission]

    def get_object(self, pk):
        try:
            return Ventilator.objects.get(pk=pk)
        except Ventilator.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ventilator = self.get_object(pk)
        serializer = self.serializer_class(ventilator)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        ventilator = self.get_object(pk)
        serializer = self.serializer_class(ventilator, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


    def delete(self, request, pk, format=None):
        ventilator = self.get_object(pk)
        ventilator.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Dashboard(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/dashboard.html'

    def get(self, request, format=None):
        demands = []
        for order in Order.objects.filter(active=True):
            if order.requesting_hospital:
                demands.append(order.requesting_hospital.address)

        supplies = []
        for hospital in Hospital.objects.all():
            ventilatorCount = Ventilator.objects.filter(state=Ventilator.State.Available.name).filter(owning_hospital=hospital).count()
            if (ventilatorCount > 0):
                supplies.append(hospital.address)

        transits = []
        for order in Order.objects.all():
            ventilators = order.ventilator_set.all()
            if ventilators.count() > 0 and ventilators.first().state == Ventilator.State.InTransit.name:
                transits.append(order.requesting_hospital.address)

        return Response({
            'demands': demands,
            'supplies': supplies,
            'transits': transits
        })

    @transaction.atomic
    def post(self, request, format=None):
        active_orders = Order.objects.filter(active=True)
        hospitals = Hospital.objects.all()
        hospitals_of_orders = [Hospital.objects.filter(id = order.requesting_hospital.id)[0] for order in active_orders]
        orders = list(zip(active_orders, hospitals_of_orders))

        num_ventilators = [Ventilator.objects.filter(current_hospital=hospital.id).filter(state=Ventilator.State.Available.name).count() for hospital in hospitals]
        htov = list(zip(hospitals, num_ventilators))

        sys_params = SystemParameters.getInstance()

        allocations = algorithm.allocate(orders, htov, sys_params)  # type: list[tuple[int, int, int]]

        batch_id = ShipmentBatches.getInstance().max_batch_id
        for allocation in allocations:
            sender, amount, receiver = allocation[0], allocation[1], allocation[2]
            order = Order.objects.filter(active=True).filter(requesting_hospital=receiver).last()
            batch_id += 1

            Ventilator.objects.filter(
                current_hospital=sender
            ).filter(
                state=Ventilator.State.Available.name
            ).update(state=Ventilator.State.Requested.name, batch_id=batch_id, order=order)

            # We were only able to partially fulfil the request, so we add a new order
            # with the remaining amount
            if order.num_requested > amount:
                new_order = Order(num_requested=order.num_requested - amount, requesting_hospital=Hospital.objects.get(id=receiver), auto_generated=True)
                new_order.save()
            order.active = False
            order.sending_hospital = Hospital.objects.get(pk=sender)
            order.date_allocated = datetime.now()
            order.save()
            # notifications.send_ventilator_notification(Hospital.objects.get(id=sender), Hospital.objects.get(id=receiver), amount)


        ShipmentBatches.update(batch_id)

        return HttpResponseRedirect(reverse('sys-dashboard', request=request, format=format))

@api_view(['POST'])
@permission_classes([IsAuthenticated&SystemOperatorPermission])
def reset_db(request, format=None):
    Order.objects.all().delete()
    Hospital.objects.all().delete()
    Ventilator.objects.all().delete()
    HospitalGroup.objects.all().delete()
    User.objects.all().delete()
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
    model_nums = [
        "Medtronic Portable",
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
    hg_user.set_password("te$t1234")
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
        h_user.set_password("te$t1234")
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

    params = SystemParameters.getInstance()
    params.destination_reserve = 10.0
    params.strategic_reserve = 10.0
    params.save()
    sys_oper_user = User(
            user_type=User.UserType.SystemOperator.name,
            email="sys_admin_covid@gmail.com",
            username="sys_admin"
        )
    sys_oper_user.set_password("te$t1234")
    sys_oper_user.save()
    sys_oper = SystemOperator(
        name="admin",
        user=User.objects.get(pk=sys_oper_user.id)
    )
    sys_oper.save()
    return HttpResponseRedirect(reverse('login', request=request))

class SystemSettings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/settings.html'

    def get(self, request):
        serializer = SystemParametersSerializer(SystemParameters.getInstance())
        return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

    def post(self, request):
        serializer = SystemParametersSerializer(SystemParameters.getInstance(), data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

class SystemDemand(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/demand.html'

    def get(self, request):
        orders = Order.objects.filter(active=True)
        return Response({'orders': orders, 'style': {'template_pack': 'rest_framework/vertical/'}})

class SystemSupply(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/supply.html'

    def get(self, request):
        supply_list = []
        for hospital in Hospital.objects.all():
            hospital_supply_list = type('test', (object,), {})()
            hospital_supply_list.name = hospital.name
            hospital_supply_list.owning_hospital_group = hospital.hospital_group.name
            available_ventilators = Ventilator.objects.filter(current_hospital=hospital).filter(state=Ventilator.State.Available.name)
            hospital_supply_list.ventilator_supply = available_ventilators.count()
            hospital_supply_list.model_nums = {ventilator.model_num for ventilator in available_ventilators}
            hospital_supply_list.monetary_value = sum(ventilator.monetary_value for ventilator in available_ventilators) 
            supply_list.append(hospital_supply_list)
        return Response({'supply_list': supply_list, 'style': {'template_pack': 'rest_framework/vertical/'}})

class SystemSourceReserve(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/strategic_reserve.html'

    def get(self, request):
        serializer = SystemParametersSerializer(SystemParameters.getInstance())
        return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

class SystemDestinationReserve(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/destination_reserve.html'

    def get(self, request):
        dst_reserve_list = []
        for order in Order.objects.all():
            count = Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name).count()
            if count == 0:
                continue
            dst_reserve_order = type('test', (object,), {})()
            dst_reserve_order.dst_hospital = order.requesting_hospital.name
            dst_reserve_order.src_hospital = order.sending_hospital.name
            dst_reserve_order.parent_hospital = order.requesting_hospital.hospital_group.name
            dst_reserve_order.quantity = count
            dst_reserve_list.append(dst_reserve_order)
        return Response({'dst_reserve_list': dst_reserve_list, 'style': {'template_pack': 'rest_framework/vertical/'}})

class HospitalCEO(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalGroupPermission]
    template_name = 'hospital_group/dashboard.html'

    def get(self, request, format=None):
        hospitals = Hospital.objects.filter(hospital_group=HospitalGroup.objects.get(user=request.user)).all()
        requested_ventilators = Ventilator.objects.filter(
            state=Ventilator.State.Requested.name
        ).filter(
            current_hospital__in=[hospital.id for hospital in hospitals]
        )

        ventRequests = []

        # If any ventilators are requested, let the user know
        if requested_ventilators:
            # Present notifications by batch as opposed to by individual ventilators
            batchid_to_ventilators = defaultdict(list)
            for ventilator in requested_ventilators:
                batchid_to_ventilators[ventilator.batch_id].append(ventilator)
            for batchid, vents in batchid_to_ventilators.items():
                if len(vents) > 0 and vents[0].order:
                    requesting_hospital = vents[0].order.requesting_hospital
                    sending_hospital = vents[0].order.sending_hospital

                    if not sending_hospital:
                        sending_hospital = vents[0].current_hospital

                    # messages.add_message(
                    #     request,
                    #     messages.INFO,
                    #     "{} requests {} ventilator(s) from {}".format(requesting_hospital, len(vents), sending_hospital),
                    #     str(batchid)
                    # )
                    ventRequests.append({
                        'requesting_hospital': requesting_hospital,
                        'offer': "{} requests {} ventilator(s) from {}".format(requesting_hospital.name, len(vents), sending_hospital.name),
                        'batchid': str(batchid)
                    })

        return Response({"ventRequests": ventRequests})

class HospitalCEOApprove(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalGroupPermission]
    template_name = 'hospital_group/approve.html'

    def get(self, request, batchid, format=None):
        requested_ventilators = Ventilator.objects.filter(batch_id=batchid)
        ventRequest = type('test', (object,), {})()
        if (requested_ventilators.count() > 0):
            ventilator = requested_ventilators.first()
            if (ventilator.state == Ventilator.State.Requested.name and ventilator.order and ventilator.current_hospital.hospital_group == HospitalGroup.objects.get(user=request.user)):
                ventRequest.requesting_hospital = ventilator.order.requesting_hospital.name
                sending_hospital = ventilator.order.sending_hospital

                if not sending_hospital:
                    sending_hospital = ventilator.current_hospital

                ventRequest.offer = "{} requests {} ventilator(s) from {}".format(ventRequest.requesting_hospital, requested_ventilators.count(), sending_hospital.name)
                ventRequest.batchid = batchid

        return Response({'ventRequest': ventRequest})
