from rest_framework.routers import DefaultRouter

from depository.apps.reception.views import ReceptionViewSet, ReportViewSet, \
    BackUpViewSet, DeliveryViewSet, AdministrationViewSet

router = DefaultRouter()
router.register('reception', ReceptionViewSet, 'reception')
router.register('delivery', DeliveryViewSet, 'delivery')
router.register('report', ReportViewSet, 'report')
router.register('administration', AdministrationViewSet, 'administration')
router.register('backup', BackUpViewSet, 'backup')
