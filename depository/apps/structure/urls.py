from rest_framework.routers import DefaultRouter

from depository.apps.structure.views import StructureViewSet

router = DefaultRouter()
router.register('structure', StructureViewSet, 'structure')
