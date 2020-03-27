from rest_framework import serializers
from webapp.models import Ventilator


class VentilatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ventilator
        fields = ['id', 'model_num', 'state']
