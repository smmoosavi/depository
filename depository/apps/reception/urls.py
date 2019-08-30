from rest_framework.routers import DefaultRouter

from depository.apps.reception.views import ReceptionViewSet, ReportViewSet, \
    BackUpViewSet

router = DefaultRouter()
router.register('reception', ReceptionViewSet, 'reception')
router.register('delivery', ReportViewSet, 'delivery')
router.register('report', ReportViewSet, 'report')
router.register('backup', BackUpViewSet, 'backup')
