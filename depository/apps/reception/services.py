from depository.apps.reception.models import Pack
from depository.apps.structure.models import Cell


class CellAssigner:
    def assign_cell(self, size):
        assert size in [Cell.SIZE_SMALL, Cell.SIZE_LARGE]
        busy_cells = Pack.objects.filter(
            delivery__exited_at__isnull=True
        ).values_list('cell', flat=True)
        return Cell.objects.filter(
            is_healthy=True
        ).exclude(
            pk__in=busy_cells
        ).order_by(
            'row__cabinet__code', 'row__code'
        ).first()
