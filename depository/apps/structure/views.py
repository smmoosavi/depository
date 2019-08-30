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
    queryset = Cell.objects.all()

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

        cabinet, row, cell = CodeHelper().to_code(self.kwargs[lookup_url_kwarg])
        query = {'code': cell, 'row__code': row, 'row__cabinet__code': cabinet}
        obj = get_object_or_404(queryset, **query)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=['POST'], detail=True)
    def deliver_to_store(self, request, pk):
        cell = self.get_object()
        delivery = Pack.objects.get(cell=cell, delivery__exited_at__isnull=True).delivery
        delivery.exited_at = timezone.now()
        delivery.exit_type = Delivery.DELIVERED_TO_STORE
        delivery.save()
        return Response({}, status=status.HTTP_200_OK)


class RowViewSet(CellViewSet, ChangeStatusMixin):
    permission_classes = [IsAdmin]


class StructureViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CabinetSerializer
    permission_classes = [IsAdmin]
