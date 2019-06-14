from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from depository.apps.structure.serializers import StructureCreateSerializer


class StructureViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = StructureCreateSerializer

    @action(methods=['POST'], detail=False)
    def change_cell_status(self, request):
        # TODO: change is_healthy of a cell
        pass

    @action(detail=False)
    def overview(self, request):
        # TODO: return overview of depository includes cabinets, rows, cells
        pass
