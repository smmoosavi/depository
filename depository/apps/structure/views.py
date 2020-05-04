# Create your views here.
from django.conf import settings
from django.db.models import Max, Min
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.reception.models import Delivery, Pack
from depository.apps.structure.helpers import CodeHelper, StructureHelper, CellHelper, ConstantHelper
from depository.apps.structure.models import Cell, Cabinet
from depository.apps.structure.serializers import CabinetCreateSerializer, \
    StatusSerializer, CabinetSerializer, CellSerializer, CabinetExtendSerializer
from depository.apps.utils.permissions import IsAdmin


class ChangeStatusMixin:
    @action(methods=['POST'], detail=False)
    def change_status(self, request):
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CabinetViewSet(GenericViewSet, CreateModelMixin, ChangeStatusMixin,
                     ListModelMixin, DestroyModelMixin):
    permission_classes = [IsAdmin]
    queryset = Cabinet.objects.all()
    lookup_field = 'code'

    def get_serializer_class(self):
        if self.action == 'create':
            return CabinetCreateSerializer
        elif self.action == 'extend':
            return CabinetExtendSerializer
        else:
            return CabinetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cabinet_serializer = CabinetSerializer(instance=serializer.instance)
        headers = self.get_success_headers(cabinet_serializer.data)
        return Response(
            cabinet_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(methods=['POST'], detail=True)
    def extend(self, request, code):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, cabinet=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        obj.refresh_from_db()
        cabinet_serializer = CabinetSerializer(instance=obj)
        headers = self.get_success_headers(cabinet_serializer.data)
        return Response(
            cabinet_serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    @action(methods=['POST'], detail=True)
    def print(self, request, code):
        obj = self.get_object()
        sh = StructureHelper()
        sh.print(obj)
        return Response({}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if not Pack.objects.filter(cell__row__cabinet=instance).exists():
            instance.delete()
        else:
            raise ValidationError("You can't delete it because this cabinet is used while ago")


class CellViewSet(GenericViewSet, ChangeStatusMixin, RetrieveModelMixin):
    permission_classes = [IsAdmin]
    queryset = Cell.objects.all()
    serializer_class = CellSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        cabinet, row, cell = CodeHelper().to_code(
            self.kwargs[lookup_url_kwarg])
        query = {'code': cell, 'row__code': row, 'row__cabinet__code': cabinet}
        obj = get_object_or_404(queryset, **query)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=['POST'], detail=True)
    def deliver_to_store(self, request, pk):
        cell = self.get_object()
        delivery = Pack.objects.get(cell=cell,
                                    delivery__exited_at__isnull=True).delivery
        delivery.exited_at = timezone.now()
        delivery.exit_type = Delivery.DELIVERED_TO_STORE
        delivery.save()
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        cell = self.get_object()
        cabinet = cell.row.cabinet
        agg_cells = Cell.objects.filter(row__cabinet=cabinet)
        cell_code_max = agg_cells.aggregate(m=Max('code'))['m']
        cell_code_min = agg_cells.aggregate(m=Min('code'))['m']
        is_asc = None
        if cell_code_max == cell.code:
            is_asc = False
        elif cell_code_min == cell.code:
            is_asc = True
        else:
            raise ValidationError(_("You should select a cell from first or last column"))
        cabinet.is_asc = is_asc
        cabinet.order = 0
        cabinet.save()
        Cell.objects.filter(row__cabinet=cabinet).update(is_fav=False)
        cell.is_fav = True
        cell.save()
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def print(self, request, pk):
        cell = self.get_object()
        CellHelper().print(cell)
        return Response({}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def free(self, request, pk):
        cell = self.get_object()
        packs = Pack.objects.filter(
            cell=cell,
            delivery__exited_at__isnull=True
        )
        for pack in packs:
            delivery = pack.delivery
            delivery.exited_at = timezone.now()
            delivery.exit_type = 0
            delivery.giver_id = 1
            delivery.save()
        return Response({}, status=status.HTTP_200_OK)


class RowViewSet(CellViewSet, ChangeStatusMixin):
    permission_classes = [IsAdmin]


class StructureViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CabinetSerializer
    permission_classes = [IsAdmin]


class ConfigViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        result = {}
        for idx, item in enumerate(settings.FARSI_CHARS):
            result[idx] = item
        return Response({
            'token': ConstantHelper().get(settings.CONST_BLINKID_TOKEN, ""),
            'row_code_mapping': result
        })
