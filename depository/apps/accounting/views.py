# Create your views here.
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet


class AccountingViewSet(GenericViewSet):
    @action(methods=['POST'], detail=False)
    def import_users(self, request):
        # TODO:
        pass
