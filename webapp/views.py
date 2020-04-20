import csv
import io
import os
from collections import defaultdict
from datetime import date, datetime
import pdb

from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
from webapp.models import Allocation, Hospital, HospitalGroup, Request, Offer, User, UserRole, Ventilator, VentilatorModel, Shipment, System, SystemParameters, Supplier
from webapp.permissions import HospitalPermission, HospitalGroupPermission, SystemPermission
from webapp.serializers import SystemParametersSerializer, VentilatorSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request, format=None):
    last_role = UserRole.get_default_role(request.user)
    if last_role == None:
        last_role = UserRole.objects.filter(assigned_user=request.user).first()
        UserRole.make_default_role(request.user, last_role)

    if last_role.supplier != None:
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))
    elif last_role.hospital_group != None:
        print('Hospital Group')
        # return HttpResponseRedirect(reverse('ceo-dashboard', request=request, format=format))
    elif last_role.hospital != None:
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))
    else:
        return HttpResponseRedirect(reverse('sys-dashboard', request=request, format=format))

    return Response(status=status.HTTP_204_NO_CONTENT)

class RequestCredentials(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'registration/request_credentials.html'

    def validate_signup(self, request_data):
        errors = []
        fields = ['username', 'email', 'entity_type', 'entity_id']
        displayFields = {
            'username': 'Username',
            'email': 'Email',
            'entity_type': 'Entity Type',
            'entity_id': 'Entity ID'
        };
        # First, verify that all fields have been given. Deal with this validation
        for field in fields:
            if request_data.get(field, '') == '':
                errors.append(displayFields[field] + ' has not been provided')
        if (len(errors) != 0):
            return errors
        if User.objects.filter(username=request_data.get('username')).count() == 1:
            errors.append('Username has been taken')

        try:
            validate_email(request_data.get('email'))
            if User.objects.filter(email=request_data.get('email')).count() == 1:
                errors.append('Account with this email has already been created')
        except ValidationError:
            errors.append('Please provide a valid email')

        entity_types = request_data.getlist('entity_type')
        entity_ids = request_data.getlist('entity_id')

        for entity_id, entity_type in zip(entity_ids, entity_types):
            if entity_id == '':
                errors.append('Blank Entity ID given for ' + entity_type)
            else:
                if entity_type == 'Hospital':
                    try:
                        Hospital.objects.get(pk=int(entity_id))
                    except Hospital.DoesNotExist:
                        errors.append('No Hospital found for ID ' + entity_id)
                elif entity_type == 'Hospital Group':
                    try:
                        HospitalGroup.objects.get(pk=int(entity_id))
                    except:
                        errors.append('No Hospital Group found for ID ' + entity_id)
                elif entity_type == 'Supplier':
                    try:
                        Supplier.objects.get(pk=int(entity_id))
                    except Supplier.DoesNotExist:
                        errors.append('No Supplier found for ID ' + entity_id)
                else:
                    try:
                        System.objects.get(pk=int(entity_id))
                    except System.DoesNotExist:
                        errors.append('No System found for ID ' + entity_id)

        return errors

    def get(self, request):
        hospitals = Hospital.objects.filter(is_valid=True)
        hospitalGroups = HospitalGroup.objects.filter(is_valid=True)
        suppliers = Supplier.objects.filter(is_valid=True)
        systems = System.objects.filter(is_valid=True)

        return Response({
            'hospitals': hospitals,
            'hospitalGroups': hospitalGroups,
            'suppliers': suppliers,
            'systems': systems,
            'style': {'template_pack': 'rest_framework/vertical/'}
        })

    def post(self, request):
        errors = self.validate_signup(request.data)
        if len(errors) != 0:
            hospitals = Hospital.objects.filter(is_valid=True)
            hospitalGroups = HospitalGroup.objects.filter(is_valid=True)
            suppliers = Supplier.objects.filter(is_valid=True)
            systems = System.objects.filter(is_valid=True)
            return Response({
                'hospitals': hospitals,
                'hospitalGroups': hospitalGroups,
                'suppliers': suppliers,
                'systems': systems,
                'errors': errors,
                'style': {'template_pack': 'rest_framework/vertical/'}
            })

        username = request.data.get('username')
        email = request.data.get('email')
        entity_types = request.data.getlist('entity_type')
        entity_ids = request.data.getlist('entity_id')
        user = User(
            email=email,
            username=username,
            inserted_at=datetime.now(),
            updated_at=datetime.now()
        )
        user.save()

        for e_id, e_type in zip(entity_ids, entity_types):
            if e_type == 'Hospital':
                hospital = Hospital.objects.get(pk=int(e_id))
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=user,
                    hospital=hospital,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
                hospital.updated_by_user = user
                hospital.save()
            elif e_type == 'Hospital Group':
                hospital_group = HospitalGroup.objects.get(pk=int(e_id))
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=user,
                    hospital_group=hospital_group,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
                hospital_group.updated_by_user = user
                hospital_group.save()
            elif e_type == 'Supplier':
                supplier = Supplier.objects.get(pk=int(e_id))
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=user,
                    supplier=supplier,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
                supplier.updated_by_user = user
                supplier.save()
            else:
                system = System.objects.get(pk=int(e_id))
                UserRole.objects.create(
                    user_role=UserRole.Role.NoRole.name,
                    assigned_user=user,
                    system=system,
                    granted_by_user=user,
                    inserted_by_user=user,
                    updated_by_user=user
                )
                system.updated_by_user = user
                system.save()
        return HttpResponseRedirect(reverse('login', request=request))

# class Requests(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&HospitalPermission]
#     template_name = 'hospital/requested_orders.html'

#     # Gives all of your requested ventilators + ventilator orders you have out.
#     def get(self, request, format=None):
#         hospital = Hospital.objects.get(pk=request.hospital_id)
#         # Demand ventilators should also be segmented? 
#         all_ventilator_requests = list(Request.objects.filter(hospital=hospital))
#         open_requests = []
#         reserve_demand_orders = []
#         requested_reserve_demand_orders = []
#         for request in all_ventilator_requests:
#             if request.status == Request.Status.Open:
#                 open_requests.append(request)
#             if Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name).count() > 0:
#                 reserve_demand_orders.append(order)
#             if Ventilator.objects.filter(order=order).filter(state=Ventilator.State.RequestedReserve.name).count() > 0:
#                 requested_reserve_demand_orders.append(order)

#         return Response({
#             'active_demand_orders': active_demand_orders,
#             'reserve_demand_orders': reserve_demand_orders,
#             'requested_reserve_demand_orders': requested_reserve_demand_orders
#         })

#     def post(self, request, format=None):
#         hospital = Hospital.objects.get(user=request.user)
#         order = Order(
#             num_requested=request.data['num_requested'],
#             time_submitted=datetime.now(),
#             active=True,
#             auto_generated=False,
#             requesting_hospital=hospital,
#         )
#         order.save()
#         return HttpResponseRedirect(reverse('requested-order', request=request))


class Offers(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/offers.html'

    def get(self, request, format=None):
        last_role = UserRole.get_default_role(request.user)
        hospital = last_role.hospital
        offers = list(Offer.objects.filter(hospital=hospital).filter(is_valid=True).filter(status=Offer.Status.Closed.name))
        openOffers = Offer.objects.filter(hospital=hospital).filter(is_valid=True).filter(status=Offer.Status.Open.name)
        if len(openOffers) > 0:
            offers.append(openOffers.first())
        return Response({
            'offers': offers
        })

class AllocationView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/allocations.html'

    def get(self, request, offer_id, format=None):
        allocations = Allocation.objects.filter(is_valid=True).filter(offer=Offer.objects.get(pk=offer_id))
        return Response({
            'allocations': allocations
        })

class ShipmentView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/shipments.html'

    def get(self, request, allocation_id, format=None):
        shipments = Shipment.objects.filter(is_valid=True).filter(allocation=Allocation.objects.get(pk=allocation_id))
        return Response({
            'shipments': shipments,
            'allocation_id': allocation_id
        })
    def post(self, request, allocation_id, format=None):
        last_role = UserRole.get_default_role(request.user)
        shipment = Shipment.objects.create(
            status=Shipment.Status.Open.name,
            allocation=Allocation.objects.get(pk=allocation_id),
            shipped_qty=request.data['num_requested'],
            inserted_by_user=request.user,
            updated_by_user=request.user,
            opened_by_user=request.user
        )
        alloc = Allocation.objects.get(pk=allocation_id)
        alloc.shipped_qty += shipment.shipped_qty
        offer = alloc.offer
        request = alloc.request 
        offer.shipped_qty += shipment.shipped_qty
        request.shipped_qty += shipment.shipped_qty
        alloc.save()
        offer.save()
        request.save()
        return HttpResponseRedirect(redirect_to='/shipments/{0}/'.format(allocation_id))
# class SuppliedOrders(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&HospitalPermission]
#     template_name = 'hospital/supplied_orders.html'

#     def get(self, request, format=None):
#         hospital = Hospital.objects.get(user=request.user)
#         all_sent_ventilator_orders = list(Order.objects.filter(sending_hospital=hospital))
#         # ventilators = [[order.ventilator_set.all()] for order in all_sent_ventilator_orders]
#         transit_orders = []
#         arrived_reserve_orders = []
#         arrived_non_reserve_orders = []
#         arrived_requested_reserve_orders = []
#         for sent_order in all_sent_ventilator_orders:
#             # Replacing num_requested with actual amt shipped for copy of object for purposes of frontend.
#             ventilators = sent_order.ventilator_set.all()
#             if ventilators.count() == 0:
#                 continue
#             sent_order.num_requested = ventilators.count()
#             if (ventilators.first().state == Ventilator.State.InTransit.name):
#                 # No Manipulation on in-transit orders
#                 transit_orders.append(sent_order)
#             else:
#                 # Ventilators are at the location.
#                 if (ventilators.filter(state=Ventilator.State.Reserve.name)):
#                     # There are reserve ventilators.
#                     arrived_reserve_orders.append(sent_order)
#                 elif (ventilators.filter(state=Ventilator.State.RequestedReserve.name)):
#                     arrived_requested_reserve_orders.append(sent_order)
#                 else:
#                     arrived_non_reserve_orders.append(sent_order)
#         return Response({
#             'transit_orders': transit_orders,
#             'arrived_reserve_orders': arrived_reserve_orders,
#             'arrived_requested_reserve_orders': arrived_requested_reserve_orders,
#             'arrived_non_reserve_orders': arrived_non_reserve_orders
#         })

class VentilatorList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&HospitalPermission]
    template_name = 'hospital/dashboard.html'

    def get(self, request, format=None):
        userRole = UserRole.get_default_role(request.user)
        ventilators = Ventilator.objects.filter(current_hospital=userRole.hospital)

        serializer = VentilatorSerializer(Ventilator.objects.first(), context={'request': request})
        return Response({'ventilators': ventilators, 'serializer': serializer})

    def post(self, request, format=None):
        # Either batch upload through CSV  or add single ventilator entry
        csv_file = request.FILES.get('file', None)
        last_role = UserRole.get_default_role(request.user)
        hospital = Hospital.objects.get(pk=last_role.hospital.id)
        if csv_file:
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)
            available_vent_ct = Ventilator.objects.filter(current_hospital=hospital).filter(Ventilator.Status.Available.name).count()
            available_vent_ct += Ventilator.objects.filter(current_hospital=hospital).filter(status=Ventilator.Status.Unavailable.name).filter(unavailable_status=Ventilator.UnavailableReason.InUse.name).count()
            src_reserve_ct = Ventilator.objects.filter(current_hospital=hospital).filter(status=Ventilator.Status.SourceReserve.name).count()
            vent_ct = available_vent_ct + src_reserve_ct
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                # Assumes serial_number, quality_level, model_type, model_mfg, monetary_value
                serial_number = column[1]
                quality_level = None
                if column[2] == 'Poor':
                    quality_level = Ventilator.Quality.Poor.name
                elif column[2] == 'Fair':
                    quality_level = Ventilator.Quality.Fair.name
                else:
                    quality_level = Ventilator.Quality.Excellent.name
                model_type = column[3]
                model_mfg = column[4]
                monetary_value = column[5]
                status = Ventilator.Status.Unavailable.name
                unavailable_status = Ventilator.UnavailableReason.InUse.name
                # We shouldn't be adding another ventilator to the supply unless the ratio is alright.
                if (src_reserve_ct / (vent_count + 1)) < (SystemParameters.getInstance().strategic_reserve / 100):
                    status = Ventilator.State.SourceReserve.name
                    src_reserve_ct += 1
                    unknown_status = None
                vent_ct += 1
                vent_model = None
                if VentilatorModel.objects.filter(model=model_type):
                    vent_model = VentilatorModel.objects.filter(model=model_type).first()
                else:
                    vent_model = VentilatorModel.objects.create(
                        model=model_type,
                        manufacturer=model_mfg,
                        monetary_value=monetary_value,
                        inserted_by_user=User.objects.get(pk=request.user.id),
                        updated_by_user=User.objects.get(pk=request.user.id)
                    )
                ventilator = Ventilator(
                    ventilator_model=vent_model,
                    serial_number=serial_number,
                    quality=quality_level,
                    monetary_value=monetary_value,
                    status=status,
                    unavailable_status=unavailable_status,
                    owning_hospital=hospital,
                    current_hospital=hospital,
                    inserted_by_user=User.objects.get(pk=request.user.id),
                    updated_by_user=User.objects.get(pk=request.user.id)
                )
                ventilator.save()
        else:
            required_fields = ['quality', 'serial_number', 'ventilator_model.model']
            for field in required_fields:
                if not request.data.get(field, None):
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            vent_model = None
            if VentilatorModel.objects.filter(model=request.data['ventilator_model.model']):
                vent_model = VentilatorModel.objects.filter(model=request.data['ventilator_model.model']).first()
            else:
                if not request.data.get('ventilator_model.manufacturer', None):
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                vent_model = VentilatorModel.objects.create(
                    model=request.data['ventilator_model.model'],
                    manufacturer=request.data['ventilator_model.manufacturer'],
                    monetary_value=int(request.data.get('ventilator_model.monetary_value', '')),
                    inserted_by_user=User.objects.get(pk=request.user.id),
                    updated_by_user=User.objects.get(pk=request.user.id)
                )
            # We'll choose the optimistic outcome and assume all unassigned ventilators will eventually become Available.
            status = Ventilator.Status.Unavailable.name
            unavailable_status = Ventilator.UnavailableReason.InUse.name
            available_vent_ct = Ventilator.objects.filter(current_hospital=hospital).filter(status=Ventilator.Status.Available.name).count()
            available_vent_ct += Ventilator.objects.filter(current_hospital=hospital).filter(status=Ventilator.Status.Unavailable.name).filter(unavailable_status=Ventilator.UnavailableReason.InUse.name).count()
            src_reserve_ct = Ventilator.objects.filter(current_hospital=hospital).filter(status=Ventilator.Status.SourceReserve.name).count()
            vent_ct = available_vent_ct + src_reserve_ct
            # If adding this ventilator messes up the strategic reserve ratio, modify it to be held in reserve
            if (src_reserve_ct / (vent_ct + 1)) < (SystemParameters.getInstance().strategic_reserve / 100):
                status = Ventilator.Status.SourceReserve.name
                unavailable_status = None
            ventilator = Ventilator(
                ventilator_model=vent_model,
                serial_number=request.data['serial_number'],
                quality=request.data['quality'],
                monetary_value=vent_model.monetary_value,
                status=status,
                unavailable_status=unavailable_status,
                owning_hospital=hospital,
                current_hospital=hospital,
                inserted_by_user=User.objects.get(pk=request.user.id),
                updated_by_user=User.objects.get(pk=request.user.id)
            )
            ventilator.save()
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def switch_entity(request, type, pk, format=None):
    if type == 'hospital-group':
        roles = UserRole.objects.filter(hospital_group=pk).filter(assigned_user=request.user)
    elif type == 'hospital':
        roles = UserRole.objects.filter(hospital=pk).filter(assigned_user=request.user)
    elif type == 'supplier':
        roles = UserRole.objects.filter(supplier=pk).filter(assigned_user=request.user)
    else:
        roles = UserRole.objects.filter(system=pk).filter(assigned_user=request.user)

    if len(roles) > 0:
        newRole = roles.first()
        UserRole.make_default_role(request.user, newRole)

    return HttpResponseRedirect(reverse('home', request=request, format=format))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated&HospitalPermission])
# def call_back_reserve(request, order_id, format=None):
#     order = Order.objects.get(pk=order_id)
#     requisitioned_ventilators = Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name)
#     for ventilator in requisitioned_ventilators:
#         ventilator.state = Ventilator.State.InTransit.name
#         ventilator.current_hospital = order.sending_hospital
#         ventilator.save()
#         # Need to send notification to receiving hospital.
#     notifications.send_requisitioned_email(order.sending_hospital, order.requesting_hospital, requisitioned_ventilators.count())
#     return HttpResponseRedirect(reverse('supplied-order', request=request))

# def change_ventilator_state(order_id, old_state, new_state):
#     order = Order.objects.get(pk=order_id)
#     allowed_ventilators = Ventilator.objects.filter(order=order).filter(state=old_state)
#     for ventilator in allowed_ventilators:
#         ventilator.state = new_state
#         ventilator.save()
#     return allowed_ventilators.count()

# @api_view(['POST'])
# @permission_classes([IsAuthenticated&HospitalPermission])
# def deploy_reserve(request, order_id, format=None):
#     count = change_ventilator_state(order_id, Ventilator.State.Reserve.name, Ventilator.State.Available.name)
#     if count == 0:
#         count = change_ventilator_state(order_id, Ventilator.State.RequestedReserve.name, Ventilator.State.Available.name)
#     available_vent_ct = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(state=Ventilator.State.Available.name).count()
#     src_reserve_ct = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(state=Ventilator.State.SourceReserve.name).count()
#     vent_ct = available_vent_ct + src_reserve_ct
#     if (src_reserve_ct / vent_ct) < SystemParameters.getInstance().strategic_reserve / 100:
#         necessary_amt = (SystemParameters.getInstance().strategic_reserve / 100) * vent_ct - src_reserve_ct
#         vents = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(state=Ventilator.State.Available.name)[:necessary_amt]
#         for vent in vents:
#             vent.state = Ventilator.State.SourceReserve.name
#             vent.save()
#     # Need to send emails to receiving hospital.
#     order = Order.objects.get(pk=order_id)
#     notifications.send_deployable_email(order.sending_hospital, order.requesting_hospital, count)
#     return HttpResponseRedirect(reverse('supplied-order', request=request))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated&HospitalPermission])
# def request_reserve(request, order_id, format=None):
#     count = change_ventilator_state(order_id, Ventilator.State.Reserve.name, Ventilator.State.RequestedReserve.name)
#     order = Order.objects.get(pk=order_id)
#     notifications.send_requested_reserve_email(order.sending_hospital, order.requesting_hospital, count)
#     return HttpResponseRedirect(reverse('requested-order', request=request))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated&HospitalPermission])
# def deny_reserve(request, order_id, format=None):
#     count = change_ventilator_state(order_id, Ventilator.State.RequestedReserve.name, Ventilator.State.Reserve.name)
#     order = Order.objects.get(pk=order_id)
#     notifications.send_denied_reserve_email(order.sending_hospital, order.requesting_hospital, count)
#     return HttpResponseRedirect(reverse('supplied-order', request=request))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @permission_classes([HospitalPermission|HospitalGroupPermission])
# def approve_ventilators(request, batchid, format=None):
#     ventilators = Ventilator.objects.filter(ventilator_batch=VentilatorBatch.objects.get(pk=batchid))
#     # TODO(hacky): HospitalGroup and Hospital should not be using the same endpoint
#     # when they're using it for different functionalities
#     if request.user.user_type == User.UserType.Hospital.name:
#         reserve_amt = 0
#         # This means it wasn't a requisition
#         if not ventilators.first().order.sending_hospital == Hospital.objects.get(user=request.user):
#             reserve_amt = SystemParameters.getInstance().destination_reserve / 100  * len(ventilators)
#         # So there is some ventilators.count()
#         # Src Rsv calc, must happen regardless of requisition.
#         potential_available_ventilators_ct = ventilators.count() - reserve_amt
#         available_vent_ct = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(state=Ventilator.State.Available.name).count()
#         src_reserve_ct = Ventilator.objects.filter(current_hospital=Hospital.objects.get(user=request.user)).filter(state=Ventilator.State.SourceReserve.name).count()
#         new_src_reserve_ct = 0
#         vent_ct = potential_available_ventilators_ct + available_vent_ct + src_reserve_ct
#         if (src_reserve_ct / vent_ct) < (SystemParameters.getInstance().strategic_reserve / 100):
#             new_src_reserve_ct = (SystemParameters.getInstance().strategic_reserve / 100) * (vent_ct) - src_reserve_ct
#         reserve_ventilator_count = 0
#         src_reserve_ventilator_count = 0

#         for vent in ventilators:
#             if vent.state == Ventilator.State.InTransit.name:
#                 if reserve_ventilator_count < reserve_amt:
#                     vent.state = Ventilator.State.Reserve.name
#                     reserve_ventilator_count += 1
#                 elif src_reserve_ventilator_count < new_src_reserve_ct:
#                     vent.state = Ventilator.State.SourceReserve.name
#                     src_reserve_ventilator_count += 1
#                 else:
#                     vent.state = Ventilator.State.Available.name
#             vent.save()
#     elif request.user.user_type == User.UserType.HospitalGroup.name:
#         for vent in ventilators:
#             if vent.state == Ventilator.State.Requested.name:
#                 vent.state = Ventilator.State.InTransit.name
#                 vent.current_hospital = vent.order.requesting_hospital
#             vent.save()
#         order = ventilators[0].order
#         order.date_fulfilled = datetime.now()
#         order.save()
#     return HttpResponseRedirect(reverse('home', request=request, format=format))


class VentilatorDetail(APIView):
    serializer_class = VentilatorSerializer
    permission_classes = [IsAuthenticated&HospitalPermission]

    def get_object(self, pk):
        try:
            return Ventilator.objects.get(pk=pk)
        except Ventilator.DoesNotExist:
            raise Http404

    # def get(self, request, pk, format=None):
    #     ventilator = self.get_object(pk)
    #     serializer = self.serializer_class(ventilator)
    #     return Response(serializer.data)

    def put(self, request, pk, format=None):
        ventilator = self.get_object(pk)
        serializer = self.serializer_class(ventilator, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return HttpResponseRedirect(reverse('ventilator-list', request=request, format=format))

    # def delete(self, request, pk, format=None):
    #     ventilator = self.get_object(pk)
    #     ventilator.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class Dashboard(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated&SystemPermission]
    template_name = 'sysoperator/dashboard.html'

    def get(self, request, format=None):
        offers = []
        for offer in Offer.objects.filter(status=Offer.Status.Approved):
            if offer.hospital:
                offers.append(offer.hospital.address)
            else:
                offers.append(offer.supplier.address)

        requests = []
        for request in Request.objects.filter(status=Request.Status.Approved.name):
            requests.append(request.hospital.address)

        transits = []
        for shipment in Shipment.objects.filter(status=Shipment.Status.Shipped.name):
            transits.append(shipment.allocation.request.hospital.address)
        return Response({
            'demands': requests,
            'supplies': offers,
            'transits': transits
        })

    @transaction.atomic
    def post(self, request, format=None):

        hospitals = Hospital.objects.all()
        htov = []
        requests = []
        # One outstanding order, multiple outstanding requests.
        for hospital in hospitals:
            offer = Offer.objects.filter(hospital=hospital).filter(is_valid=True).filter(status=Offer.Status.Open.name).first()
            if offer:
                htov.append((hospital, offer.offered_qty-offer.allocated_qty))
            reqs = Request.objects.filter(hospital=hospital).filter(is_valid=True).filter(status=Request.Status.Open.name)
            if reqs:
                num_req = 0
                for req in reqs:
                    num_req += (req.requested_qty - req.allocated_qty)
                requests.append((num_req, hospital))
        sys_params = SystemParameters.getInstance()
        allocations = algorithm.allocate(requests, htov, sys_params)  # type: list[tuple[int, int, int]]
        for allocation in allocations:
            sender, amount, receiver = allocation[0], allocation[1], allocation[2]
            receiver_reqs = Request.objects.filter(hospital=receiver).filter(is_valid=True).filter(status=Request.Status.Open.name)
            offer = Offer.objects.filter(hospital=sender).filter(is_valid=True).filter(status=Offer.Status.Open.name).first()
            for req in receiver_reqs:
                if amount == 0:
                    break
                if req.requested_qty == req.allocated_qty:
                    continue
                num_assigned = min(req.requested_qty - req.allocated_qty, amount)
                req.allocated_qty += num_assigned
                offer.allocated_qty += num_assigned
                offer.save()
                req.save()
                Allocation.objects.create(
                    request=req,
                    offer=offer,
                    status=Allocation.Status.Approved.name,
                    allocated_qty=num_assigned,
                    opened_by_user=request.user,
                    inserted_by_user=request.user,
                    updated_by_user=request.user,
                    approved_by_user=request.user
                )
                amount -= num_assigned
            # order = Order.objects.filter(active=True).filter(requesting_hospital=receiver).last()
            # batch = VentilatorBatch(order=order)
            # batch.save()
            # for vent in Ventilator.objects.filter(current_hospital=sender).filter(state=Ventilator.State.Available.name)[:amount]:
            #     vent.state = Ventilator.State.Requested.name
            #     vent.ventilator_batch = VentilatorBatch.objects.get(pk=batch.id)
            #     vent.order = order
            #     vent.save()
            # # We were only able to partially fulfil the request, so we add a new order
            # # with the remaining amount
            # if order.num_requested > amount:
            #     new_order = Order(num_requested=order.num_requested - amount, requesting_hospital=Hospital.objects.get(id=receiver), auto_generated=True)
            #     new_order.save()
            # order.active = False
            # order.sending_hospital = Hospital.objects.get(pk=sender)
            # order.date_allocated = datetime.now()
            # order.save()
        # notifications.send_ventilator_notification(Hospital.objects.get(id=sender), Hospital.objects.get(id=receiver), amount)

        return HttpResponseRedirect(reverse('sys-dashboard', request=request, format=format))

@api_view(['POST'])
@permission_classes([IsAuthenticated&SystemPermission])
def reset_db(request, format=None):
    return HttpResponseRedirect(reverse('login', request=request))

# class SystemSettings(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&SystemPermission]
#     template_name = 'sysoperator/settings.html'

#     def get(self, request):
#         serializer = SystemParametersSerializer(SystemParameters.getInstance())
#         return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

#     def post(self, request):
#         serializer = SystemParametersSerializer(SystemParameters.getInstance(), data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#         return Response({'serializer': serializer, 'style': {'template_pack': 'rest_framework/vertical/'}})

# class SystemDemand(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&SystemPermission]
#     template_name = 'sysoperator/demand.html'

#     def get(self, request):
#         orders = Order.objects.filter(active=True)
#         return Response({'orders': orders, 'style': {'template_pack': 'rest_framework/vertical/'}})

# class SystemSupply(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&SystemPermission]
#     template_name = 'sysoperator/supply.html'

#     def get(self, request):
#         supply_list = []
#         for hospital in Hospital.objects.all():
#             hospital_supply_list = type('test', (object,), {})()
#             hospital_supply_list.name = hospital.name
#             hospital_supply_list.owning_hospital_group = hospital.hospital_group.name
#             available_ventilators = Ventilator.objects.filter(current_hospital=hospital).filter(state=Ventilator.State.Available.name)
#             hospital_supply_list.ventilator_supply = available_ventilators.count()
#             hospital_supply_list.model_nums = {ventilator.model_num for ventilator in available_ventilators}
#             hospital_supply_list.monetary_value = sum(ventilator.monetary_value for ventilator in available_ventilators) 
#             supply_list.append(hospital_supply_list)
#         return Response({'supply_list': supply_list, 'style': {'template_pack': 'rest_framework/vertical/'}})

# class SystemSourceReserve(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&SystemPermission]
#     template_name = 'sysoperator/strategic_reserve.html'

#     def get(self, request):
#         src_reserve_lst = []
#         for hospital in Hospital.objects.all():
#             reserve_obj = type('test', (object,), {})()
#             src_reserve = Ventilator.objects.filter(current_hospital=hospital).filter(state=Ventilator.State.SourceReserve.name)
#             if src_reserve.count() == 0:
#                 continue
#             reserve_obj.src_hospital = hospital.name
#             reserve_obj.parent = hospital.hospital_group.name
#             reserve_obj.quantity = src_reserve.count()
#             reserve_obj.model_nums = {ventilator.model_num for ventilator in src_reserve}
#             src_reserve_lst.append(reserve_obj)
#         return Response({'ventilators': src_reserve_lst, 'style': {'template_pack': 'rest_framework/vertical/'}})

# class SystemDestinationReserve(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&SystemPermission]
#     template_name = 'sysoperator/destination_reserve.html'

#     def get(self, request):
#         dst_reserve_list = []
#         for order in Order.objects.all():
#             count = Ventilator.objects.filter(order=order).filter(state=Ventilator.State.Reserve.name).count()
#             if count == 0:
#                 continue
#             dst_reserve_order = type('test', (object,), {})()
#             dst_reserve_order.dst_hospital = order.requesting_hospital.name
#             dst_reserve_order.src_hospital = order.sending_hospital.name
#             dst_reserve_order.parent_hospital = order.requesting_hospital.hospital_group.name
#             dst_reserve_order.quantity = count
#             dst_reserve_list.append(dst_reserve_order)
#         return Response({'dst_reserve_list': dst_reserve_list, 'style': {'template_pack': 'rest_framework/vertical/'}})

# class HospitalCEO(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&HospitalGroupPermission]
#     template_name = 'hospital_group/dashboard.html'

#     def get(self, request, format=None):
#         hospitals = Hospital.objects.filter(hospital_group=HospitalGroup.objects.get(user=request.user)).all()
#         requested_ventilators = Ventilator.objects.filter(
#             state=Ventilator.State.Requested.name
#         ).filter(
#             current_hospital__in=[hospital.id for hospital in hospitals]
#         )

#         ventRequests = []

#         # If any ventilators are requested, let the user know
#         if requested_ventilators:
#             # Present notifications by batch as opposed to by individual ventilators
#             batchid_to_ventilators = defaultdict(list)
#             for ventilator in requested_ventilators:
#                 batchid_to_ventilators[ventilator.ventilator_batch.id].append(ventilator)
#             for batchid, vents in batchid_to_ventilators.items():
#                 if len(vents) > 0 and vents[0].order:
#                     requesting_hospital = vents[0].order.requesting_hospital
#                     sending_hospital = vents[0].order.sending_hospital

#                     if not sending_hospital:
#                         sending_hospital = vents[0].current_hospital

#                     # messages.add_message(
#                     #     request,
#                     #     messages.INFO,
#                     #     "{} requests {} ventilator(s) from {}".format(requesting_hospital, len(vents), sending_hospital),
#                     #     str(batchid)
#                     # )
#                     ventRequests.append({
#                         'requesting_hospital': requesting_hospital,
#                         'offer': "{} requests {} ventilator(s) from {}".format(requesting_hospital.name, len(vents), sending_hospital.name),
#                         'batchid': str(batchid)
#                     })

#         return Response({"ventRequests": ventRequests})

# class HospitalCEOApprove(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&HospitalGroupPermission]
#     template_name = 'hospital_group/approve.html'

#     def get(self, request, batchid, format=None):
#         requested_ventilators = Ventilator.objects.filter(ventilator_batch=VentilatorBatch.objects.get(pk=batchid))
#         if (requested_ventilators.count() > 0):
#             ventilator = requested_ventilators.first()
#             if (ventilator.state == Ventilator.State.Requested.name and ventilator.order and ventilator.current_hospital.hospital_group == HospitalGroup.objects.get(user=request.user)):
#                 ventRequest = type('test', (object,), {})()
#                 ventRequest.requesting_hospital = ventilator.order.requesting_hospital.name
#                 sending_hospital = ventilator.order.sending_hospital

#                 if not sending_hospital:
#                     sending_hospital = ventilator.current_hospital

#                 ventRequest.offer = "{} requests {} ventilator(s) from {}".format(ventRequest.requesting_hospital, requested_ventilators.count(), sending_hospital.name)
#                 ventRequest.batchid = batchid

#                 return Response({'ventRequest': ventRequest})
#             else:
#                 return HttpResponseRedirect(reverse('ceo-dashboard', request=request))
#         else:
#             return HttpResponseRedirect(reverse('ceo-dashboard', request=request))

# class HospitalCEOSharedOffer(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     permission_classes = [IsAuthenticated&HospitalGroupPermission]
#     template_name = 'hospital_group/offer.html'

#     def get(self, request, batchid, format=None):
#         requested_ventilators = Ventilator.objects.filter(ventilator_batch=VentilatorBatch.objects.get(pk=batchid))
#         if (requested_ventilators.count() > 0):
#             ventilator = requested_ventilators.first()
#             if (ventilator.state == Ventilator.State.Requested.name and ventilator.order and ventilator.current_hospital.hospital_group == HospitalGroup.objects.get(user=request.user)):
#                 return Response({'ventilators': requested_ventilators})
#             else:
#                 return HttpResponseRedirect(reverse('ceo-dashboard', request=request))
#         else:
#             return HttpResponseRedirect(reverse('ceo-dashboard', request=request))
