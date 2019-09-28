# Create your views here.
import logging

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.reception.filters import DeliveryFilter
from depository.apps.reception.models import Delivery, Pack
from depository.apps.reception.serializers import ReceptionTakeSerializer, \
    ReceptionGiveSerializer, DeliverySerializer
from depository.apps.reception.services import ReceptionHelper
from depository.apps.utils.permissions import IsAdmin

logger = logging.getLogger(__name__)


class ReceptionViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ReceptionTakeSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'take':
            return ReceptionTakeSerializer
        else:
            return ReceptionGiveSerializer

    def _create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(methods=['POST'], detail=False)
    def give(self, request):
        return self._create(request)

    @action(methods=['POST'], detail=False)
    def take(self, request):
        return self._create(request)


class DeliveryViewSet(GenericViewSet, ListModelMixin):
    serializer_class = DeliverySerializer
    filter_class = DeliveryFilter
    lookup_field = 'hash_id'
    queryset = Delivery.objects.all()

    @action(methods=['GET'], detail=False)
    def old(self, request):
        threshold = timezone.now() - timezone.timedelta(days=settings.STORE_DAYS)
        deliveries = Delivery.objects.filter(
            exited_at__isnull=True, entered_at__lte=threshold
        )
        serializer = self.get_serializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def revert_exit(self, request, hash_id):
        obj = self.get_object()
        obj.exit_type = None
        obj.exited_at = None
        obj.giver = None
        obj.save()
        return Response({}, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def print(self, request):
        last_pack = Pack.objects.filter(delivery__taker=request.user).order_by('-delivery__entered_at').first()
        rh = ReceptionHelper()
        rh.print(last_pack)
        return Response({}, status.HTTP_200_OK)


class ReportViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        result = ReceptionHelper().report()
        return Response(result, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def start(self, request, *args, **kwargs):
        result = ReceptionHelper().admin_report()
        return Response(result, status=status.HTTP_200_OK)


class BackUpViewSet(GenericViewSet):
    # TODO: import and export whole database
    pass
