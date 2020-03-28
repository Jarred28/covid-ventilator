from datetime import datetime
import csv
import io

from . import notifications
from django.http import Http404, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status

from webapp.models import Hospital, Order, User, Ventilator
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

    def get(self, request, hospital, format=None):
        ventilator_orders = list(Order.objects.filter(hospital=hospital))
        return Response({'orders': ventilator_orders})

    def post(self, request, hospital, format=None):
        order = Order(
            num_requested=request.data['num_requested'],
            time_submitted=datetime.now(),
            active=True,
            auto_generated=False,
            hospital=Hospital.objects.get(pk=hospital)
        )
        order.save()
        ventilator_orders = list(Order.objects.filter(hospital=hospital))
        return Response({'orders': ventilator_orders})

class VentilatorList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/dashboard.html'

    def get(self, request, format=None):
        ventilators = Ventilator.objects.all()
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
                    owning_hospital=Hospital.objects.get(user=request.user), current_hospital=Hospital.objects.get(user=request.user)
                )
                ventilator.save()
        else:
            if not request.data.get("model_num", None) or not request.data.get("state", None):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            ventilator = Ventilator(
                model_num=request.data["model_num"], state=request.data["state"],
                owning_hospital=Hospital.objects.get(user=request.user), current_hospital=Hospital.objects.get(user=request.user)
            )
            ventilator.save()

        ventilators = Ventilator.objects.all()
        serializer = VentilatorSerializer(ventilator)
        return Response({'ventilators': ventilators, 'serializer': serializer})


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
        return Response({})

    def post(self, request, format=None):
        ## This is the algorithm endpoint
        ## Replace RHS with the algorithm call once linked in. Format is sender, amount, receiver.

        allocation_list = [[Hospital.objects.first(), 1, Hospital.objects.last()]]
        batch_id = ShipmentBatches.first().max_batch_id
        for allocation in allocation_list:
            sender = allocation[0]
            amount = allocation[1]
            receiver = allocation[2]
            requested_ventilators = Ventilator.objects.filter(current_hospital=sender).filter(state=Ventilator.State.Available.name)[:amount]
            # Extract latest order. This assumes that a hospital only has 1 active order at a time.
            order = Order.objects.filter(hospital=receiver).filter(active=True).last()
            batch_id = batch_id + 1
            for ventilator in requested_ventilators:
                ventilator.state = Ventilator.State.Requested.name
                ventilator.order = order
                ventilator.batch_id = batch_id
                ventilator.save()
            notifications.send_ventilator_notification(sender, receiver, amount)
        shipment_batch = ShipmentBatches.first()
        shipment_batch.max_batch_id = batch_id
        shipment_batch.save() 
        return Response({})
