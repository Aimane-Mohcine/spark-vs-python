# spark/serializers.py
from rest_framework import serializers
from .models import DatasetA
from .models import DatasetB
from .models import Ecart



class DatasetASerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetA
        fields = '__all__'




class DatasetBSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetB
        fields = '__all__'





class EcartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ecart
        fields = '__all__'