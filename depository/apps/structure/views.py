# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.structure.serializers import CabinetCreateSerializer, \
    StatusSerializer, CabinetSerializer


class ChangeStatusMixin:
    @action(methods=['POST'], detail=False)
    def change_status(self, request):
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: update cell status
        return Response(serializer.data, status=status.HTTP_200_OK)


class CabinetViewSet(GenericViewSet, CreateModelMixin, ChangeStatusMixin):
    serializer_class = CabinetCreateSerializer


class CellViewSet(GenericViewSet, ChangeStatusMixin):
    pass


class RowViewSet(CellViewSet, ChangeStatusMixin):
    pass


class StructureViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CabinetSerializer
