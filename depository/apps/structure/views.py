# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.structure.serializers import CabinetCreateSerializer, \
    StatusSerializer, CabinetSerializer
from depository.apps.utils.permissions import IsAdmin


class ChangeStatusMixin:

    @action(methods=['POST'], detail=False)
    def change_status(self, request):
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CabinetViewSet(GenericViewSet, CreateModelMixin, ChangeStatusMixin):
    serializer_class = CabinetCreateSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cabinet_serializer = CabinetSerializer(instance=serializer.instance)
        headers = self.get_success_headers(cabinet_serializer.data)
        return Response(cabinet_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CellViewSet(GenericViewSet, ChangeStatusMixin):
    permission_classes = [IsAdmin]


class RowViewSet(CellViewSet, ChangeStatusMixin):
    permission_classes = [IsAdmin]


class StructureViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CabinetSerializer
    permission_classes = [IsAdmin]
