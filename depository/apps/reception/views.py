# Create your views here.
import logging
import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.reception.filters import DeliveryFilter
from depository.apps.reception.models import Delivery, Pack
from depository.apps.reception.serializers import ReceptionTakeSerializer, \
    ReceptionGiveSerializer, DeliverySerializer, ReceptionGiveListSerializer
from depository.apps.reception.services import ReceptionHelper
from depository.apps.utils.rest import DepositoryPermission

logger = logging.getLogger(__name__)


class ReceptionViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ReceptionTakeSerializer
    permission_classes = [IsAuthenticated, DepositoryPermission]
    queryset = Delivery.objects.none()

    def get_serializer_class(self):
        if self.action == 'take':
            return ReceptionTakeSerializer
        elif self.action == 'give_list':
            return ReceptionGiveListSerializer
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

    @action(methods=['POST'], detail=False)
    def give_list(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deliveries = serializer.save()
        response_serializer = ReceptionGiveSerializer(deliveries, many=True)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class DeliveryViewSet(GenericViewSet, ListModelMixin):
    serializer_class = DeliverySerializer
    filter_class = DeliveryFilter
    lookup_field = 'hash_id'
    queryset = Delivery.objects.all().order_by('-entered_at')
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = request.GET.get('limit', None)
        try:
            if limit:
                queryset = queryset[:int(limit)]
        except TypeError:
            pass

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        if timezone.now() - obj.exited_at > timedelta(minutes=settings.REVERT_THRESHOLD):
            raise ValidationError(_("Revert timeout exceeded"))
        obj.exit_type = None
        obj.exited_at = None
        obj.giver = None
        obj.save()
        return Response({}, status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def reprint(self, request, hash_id):
        pack = Pack.objects.get(delivery__taker=request.user, delivery__hash_id=hash_id)
        rh = ReceptionHelper()
        rh.print(pack)
        return Response({}, status.HTTP_200_OK)


class ReportViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        result = ReceptionHelper().report()
        return Response(result, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def start(self, request, *args, **kwargs):
        result = ReceptionHelper().admin_report()
        return Response(result, status=status.HTTP_200_OK)


class AdministrationViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False)
    def export(self, *args, **kwargs):
        path = ReceptionHelper().export_data()
        return Response({'url': os.path.join(settings.EXPORT_URL, path)})

    @action(methods=['GET'], detail=False)
    def export_store(self, *args, **kwargs):
        path = ReceptionHelper().export_data(exit_type=Delivery.DELIVERED_TO_STORE)
        return Response({'url': os.path.join(settings.EXPORT_URL, path)})


class BackUpViewSet(GenericViewSet):
    # TODO: import and export whole database
    pass
