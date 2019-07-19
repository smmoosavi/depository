# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.reception.filters import DeliveryFilter
from depository.apps.reception.serializers import ReceptionTakeSerializer, \
    ReceptionGiveSerializer, DeliverySerializer


class ReceptionViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ReceptionTakeSerializer

    def get_serializer_class(self):
        if action == 'take':
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

    @action(methods=['POST'], detail=False)
    def deliver_to_store(self, request):
        # TODO:
        pass


class DeliveryViewSet(GenericViewSet, ListModelMixin):
    serializer_class = DeliverySerializer
    filter_class = DeliveryFilter


class ReportViewSet(GenericViewSet):
    # TODO: ??
    pass


class BackUpViewSet(GenericViewSet):
    # TODO: import and export whole database
    pass
