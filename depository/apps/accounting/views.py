# Create your views here.
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from depository.apps.accounting.filters import PilgrimFilter
from depository.apps.accounting.serializers import UserSerializer, \
    PilgrimSerializer


class AccountingViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False)
    def import_users(self, request):
        # TODO:
        pass


class PilgrimViewSet(GenericViewSet, ListModelMixin):
    serializer_class = PilgrimSerializer
    filter_class = PilgrimFilter
