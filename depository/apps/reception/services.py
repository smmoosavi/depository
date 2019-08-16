from django.db.models import Max, Min
from django.template.loader import render_to_string

from depository.apps.reception.models import Pack
from depository.apps.structure.models import Cell, Cabinet
from depository.apps.utils.print import PrintHelper


class CellHelper:
    def assign_cell(self, size):
        assert size in [Cell.SIZE_SMALL, Cell.SIZE_LARGE]
        busy_cells = Pack.objects.filter(
            delivery__exited_at__isnull=True
        ).values_list('cell', flat=True)
        cabinet_order = Cell.objects.filter(
            is_healthy=True
        ).exclude(
            pk__in=busy_cells
        ).order_by('row__cabinet__order').first()
        if not cabinet_order:
            return None
        cabinet_order = cabinet_order.row.cabinet.order
        for cabinet in Cabinet.objects.filter(order=cabinet_order):
            is_asc = cabinet.is_asc
            cells = Cell.objects.filter(
                is_healthy=True, row__cabinet=cabinet, size=size
            ).exclude(
                pk__in=busy_cells
            )
            if not cells:
                continue
            agg_cells = Cell.objects.filter(row__cabinet=cabinet, size=size)
            row_code_max = agg_cells.aggregate(m=Max('row__code'))['m']
            row_code_min = agg_cells.aggregate(m=Min('row__code'))['m']
            row_code_mean = (row_code_max + row_code_min) / 2
            cell_code_max = agg_cells.aggregate(m=Max('code'))['m']

            def compare(cell):
                cell_code = cell.code
                if not is_asc:
                    cell_code = cell_code_max - cell.code
                return abs(cell.row.code - row_code_mean) * 100 + cell_code

            return sorted(cells, key=compare)[0]
        return None

    def print(self, pack):
        badge_count = pack.bag_count + pack.pram_count + pack.suitcase_count
        ph = PrintHelper()
        for idx in range(badge_count):
            html = render_to_string('badge.html', {'index': idx, 'count': badge_count})
            ph.print(html)
        html = render_to_string('reciept.html', {})
        # TODO:
        ph.print(html)
