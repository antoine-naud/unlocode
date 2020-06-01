from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
 
from unlocode.api.serializers import UnlocodeSerializer
from unlocode.models import Unlocode


class UnlocodeList(ListAPIView):
    queryset = Unlocode.objects.all()
    serializer_class = UnlocodeSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id', 'locode', 'namewodiacritics',)


class UnlocodeCodeRetrieve(RetrieveAPIView):
    queryset = Unlocode.objects.all()
    lookup_field = 'locode'
    serializer_class = UnlocodeSerializer


class UnlocodeNameRetrieve(RetrieveAPIView):
    queryset = Unlocode.objects.all()
    lookup_field = 'namewodiacritics'
    serializer_class = UnlocodeSerializer
