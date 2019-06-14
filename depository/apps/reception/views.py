# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.reception.serializers import ReceptionTakeSerializer, \
    ReceptionGiveSerializer


class ReceptionViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ReceptionTakeSerializer

    def get_serializer_class(self):
        if action == 'take':
            return self.serializer_class
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
    def search(self, request):
        # TODO: search on user and delivery date
        pass

    @action(methods=['POST'], detail=False)
    def deliver_to_store(self, request):
        # TODO:
        pass


class ReportViewSet(GenericViewSet):
    # TODO: ??
    pass


class BackUpViewSet(GenericViewSet):
    # TODO: import and export whole database
    pass
