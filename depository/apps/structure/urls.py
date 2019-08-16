from rest_framework.routers import DefaultRouter

from depository.apps.reception.views import DeliveryViewSet
from depository.apps.structure.views import StructureViewSet, CabinetViewSet, \
    CellViewSet, RowViewSet

router = DefaultRouter()
router.register('cabinet', CabinetViewSet, 'cabinet')
router.register('cell', CellViewSet, 'cell')
router.register('row', RowViewSet, 'row')
router.register('delivery', DeliveryViewSet, 'delivery')
router.register('structure', StructureViewSet, 'structure')
