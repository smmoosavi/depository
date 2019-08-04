# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from depository.apps.accounting.filters import PilgrimFilter
from depository.apps.accounting.serializers import UserSerializer, \
    PilgrimSerializer, SignInSerializer


class AccountingViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False)
    def import_users(self, request):
        # TODO:
        pass


class PilgrimViewSet(GenericViewSet, ListModelMixin):
    serializer_class = PilgrimSerializer
    filter_class = PilgrimFilter


class SignInViewSet(GenericViewSet):
    serializer_class = SignInSerializer
    permission_classes = [AllowAny, ]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return Response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
