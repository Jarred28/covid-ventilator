from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from webapp.models import Ventilator
from webapp.serializers import VentilatorSerializer


@csrf_exempt
def ventilator_list(request):
    """
    List all ventilators, or create a new ventilator.
    """
    if request.method == 'GET':
        ventilators = Ventilator.objects.all()
        serializer = VentilatorSerializer(ventilators, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = VentilatorSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        serializer.save()
        return JsonResponse(serializer.data, status=201)
        
    
@csrf_exempt
def ventilator_detail(request, pk):
    """
    Retrieve, update or delete a ventilator.
    """
    try:
        ventilator = Ventilator.objects.get(pk=pk)
    except Ventilator.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = VentilatorSerializer(ventilator)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = VentilatorSerializer(ventilator, data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        serializer.save()
        return JsonResponse(serializer.data)
    elif request.method == 'DELETE':
        ventilator.delete()
        return HttpResponse(status=204)
