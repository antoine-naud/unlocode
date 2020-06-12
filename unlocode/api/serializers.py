from rest_framework import serializers
from unlocode.models import Unlocode


class UnlocodeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Unlocode
       fields = '__all__'
