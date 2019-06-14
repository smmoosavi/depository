from rest_framework.routers import DefaultRouter

from depository.apps.accounting.views import AccountingViewSet

router = DefaultRouter()
router.register('accounting', AccountingViewSet, 'accounting')
