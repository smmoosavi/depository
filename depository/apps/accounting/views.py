# Create your views here.
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_response_payload_handler

from depository.apps.accounting.filters import PilgrimFilter
from depository.apps.accounting.models import Pilgrim
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
    queryset = Pilgrim.objects.all()


class SignInViewSet(GenericViewSet):
    serializer_class = SignInSerializer
    permission_classes = [AllowAny, ]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            token = serializer.validated_data['token']
            response_data = jwt_response_payload_handler(token, user, request)

            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(
                    api_settings.JWT_AUTH_COOKIE,
                    token,
                    expires=expiration,
                    httponly=True,
                )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
