from rest_framework.routers import DefaultRouter

from depository.apps.accounting.views import AccountingViewSet, PilgrimViewSet, SignInViewSet

router = DefaultRouter()
router.register('accounting', AccountingViewSet, 'accounting')
router.register('pilgrim', PilgrimViewSet, 'pilgrim')
router.register('signin', SignInViewSet, 'signin')
