import csv
import io
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status

from . import notifications
from webapp.algorithm import algorithm
from webapp.models import Hospital, Order, User, Ventilator, ShipmentBatches
from webapp.permissions import HospitalPermission, SystemOperatorPermission
from webapp.serializers import SignupSerializer, VentilatorSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request, format=None):
    if request.user.user_type == User.UserType.Hospital.name:
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))
    if request.user.user_type == User.UserType.SystemOperator.name:
        return HttpResponseRedirect(reverse('sys-settings', request=request, format=format))
    return Response(status=status.HTTP_204_NO_CONTENT)

class RequestCredentials(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registration/request_credentials.html'

    def get(self, request):
        serializer = SignupSerializer()
        return Response({'serializer': serializer, "style": {"template_pack": "rest_framework/inline/"}})

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, "style": {"template_pack": "rest_framework/inline/"}})
        serializer.save()
        return HttpResponseRedirect(reverse('login', request=request))

class OrderInfo(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/order.html'

    def get(self, request, format=None):
        hospital = Hospital.objects.get(user=request.user)
        ventilator_orders = list(Order.objects.filter(hospital=hospital))
        return Response({'orders': ventilator_orders})

    def post(self, request, format=None):
        hospital = Hospital.objects.get(user=request.user)
        order = Order(
            num_requested=request.data['num_requested'],
            time_submitted=datetime.now(),
            active=True,
            auto_generated=False,
            hospital=hospital,
        )
        order.save()
        ventilator_orders = list(Order.objects.filter(hospital=hospital))
        return Response({'orders': ventilator_orders})

class VentilatorList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/dashboard.html'

    def get(self, request, format=None):
        ventilators = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user))

        # If any ventilators are requested, let the user know
        requested_ventilators = ventilators.filter(state=Ventilator.State.Requested.name)
        if requested_ventilators:
            # Present notifications by batch as opposed to by individual ventilators
            batchid_to_ventilators = defaultdict(list)
            for ventilator in requested_ventilators:
                batchid_to_ventilators[ventilator.batch_id].append(ventilator)
            for batchid, vents in batchid_to_ventilators.items():
                messages.add_message(request, messages.INFO, "%d ventilator(s) are requested" % len(vents), str(batchid))

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
def approve_ventilators(request, batchid, format=None):
    ventilators = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(batch_id=batchid)
    for vent in ventilators:
        if vent.state == Ventilator.State.Requested.name:
            vent.state = Ventilator.State.InTransit.name
            vent.current_hospital = vent.order.hospital
        elif vent.state == Ventilator.State.InTransit.name:
            vent.state = Ventilator.State.Available.name
        vent.save()
    return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))


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


class SystemSettings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemOperatorPermission]
    template_name = 'sysoperator/dashboard.html'

    def get(self, request, format=None):
        return Response()

    @transaction.atomic
    def post(self, request, format=None):
        active_orders = Order.objects.filter(active=True)
        hospitals = Hospital.objects.all()

        orders = [{
            "hospital": order.hospital.id,
            "num_requested": order.num_requested,
        } for order in active_orders]
        htov = [{
            "hospital": hospital.id,
            "group": hospital.hospital_group.id,
            "reputation": hospital.reputation_score,  # TODO: Reputation score may sometimes be None
            "only_within_group": hospital.within_group_only,
            "num_ventilators": Ventilator.objects.filter(current_hospital=hospital.id).filter(state=Ventilator.State.Available.name).count()
            } for hospital in hospitals]
        htog = {hospital.id: hospital.hospital_group.id for hospital in hospitals}
        allocations = algorithm.allocate(orders, htov, htog)  # type: list[tuple[int, int, int]]

        if ShipmentBatches.objects.count() == 0:
            shipment_batch = ShipmentBatches(max_batch_id=0)
            shipment_batch.save()

        batch_id = ShipmentBatches.objects.first().max_batch_id
        for allocation in allocations:
            sender, amount, receiver = allocation[0], allocation[1], allocation[2]
            order = Order.objects.filter(hospital=receiver).filter(active=True).last()
            batch_id += 1

            Ventilator.objects.filter(
                current_hospital=sender
            ).filter(
                state=Ventilator.State.Available.name
            ).update(state=Ventilator.State.Requested.name, batch_id=batch_id, order=order)

            order.active = False
            order.save()
            # notifications.send_ventilator_notification(Hospital.objects.get(id=sender), Hospital.objects.get(id=receiver), amount)

        shipment_batch = ShipmentBatches.objects.first()
        shipment_batch.max_batch_id = batch_id
        shipment_batch.save()

        return Response()
