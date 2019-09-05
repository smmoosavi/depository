from rest_framework.routers import DefaultRouter

from depository.apps.structure.views import StructureViewSet, CabinetViewSet, \
    CellViewSet, RowViewSet

router = DefaultRouter()
router.register('cabinet', CabinetViewSet, 'cabinet')
router.register('cell', CellViewSet, 'cell')
router.register('row', RowViewSet, 'row')
router.register('structure', StructureViewSet, 'structure')
