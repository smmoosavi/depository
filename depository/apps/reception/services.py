from datetime import timedelta

from django.conf import settings
from django.db.models import Max, Min, Count
from django.template.loader import render_to_string
from django.utils import timezone
from khayyam.jalali_datetime import JalaliDatetime

from depository.apps.reception.models import Pack, Delivery
from depository.apps.structure.models import Cell, Cabinet
from depository.apps.utils.print import PrintHelper


class ReceptionHelper:
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
        pilgrim = pack.delivery.pilgrim
        entered_at = JalaliDatetime(pack.delivery.entered_at).strftime("%A %d %B %H:%M")
        for idx in range(badge_count):
            html = render_to_string('badge.html', {
                'name': pilgrim.get_full_name(), 'index': idx + 1, 'count': badge_count,
                'country': pilgrim.country, 'phone': pilgrim.phone[-4:], 'entered_at': entered_at,
                'code': pack.cell.get_code()

            })
            ph.print(html)

        depository = pack.cell.row.cabinet.depository
        html = render_to_string('reciept.html', {
            'depository_name': depository.name, 'depository_address': depository.address,
            'social': settings.CONST_KEY_SOCIAL, 'phone': settings.CONST_KEY_PHONE,
            'notice': settings.CONST_KEY_NOTICE, 'entered_at': entered_at
        })
        # TODO:
        ph.print(html, 80, 100)

    def report(self):
        total_count = Delivery.objects.count()
        distribution = {'total': total_count,}
        deliveries = Delivery.objects.values('exit_type').annotate(count=Count('pk'))
        for item in deliveries:
            distribution[item['exit_type']] = item['count']

        in_house = Delivery.objects.filter(exited_at__isnull=True)
        periods = [0, 3, 6, 24, 48]
        result_in_house = {}
        for i in range(len(periods) - 1):
            end = timezone.now() - timedelta(hours=periods[i])
            start = timezone.now() - timedelta(hours=periods[i + 1])
            result_in_house[periods[i + 1]] = in_house.filter(entered_at__range=[start, end]).count()
        result = {
            'in_house': result_in_house,
            'distribution': distribution
        }
        return result
