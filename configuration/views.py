from rest_framework import viewsets

from configuration.models import Environment
from configuration.serializers import EnvironmentSerializer


class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = (
        Environment.objects.all()
        .prefetch_related("configuration_values")
        .select_related("promotes_from")
    )
    serializer_class = EnvironmentSerializer
