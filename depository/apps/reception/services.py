import random
import string
from datetime import datetime
from datetime import timedelta

import qrcode
from django.conf import settings
from django.db.models import Max, Min, Count, Q
from django.template.loader import render_to_string
from django.utils import timezone
from khayyam.jalali_datetime import JalaliDatetime

from depository.apps.reception.models import Pack, Delivery
from depository.apps.structure.models import Cell, Cabinet
from depository.apps.utils.print import PrintHelper
from depository.apps.utils.utils import Encryption


class ReceptionHelper:
    def assign_cell(self, size):
        assert size in [Cell.SIZE_SMALL, Cell.SIZE_LARGE]
        treshold = timezone.now() - timezone.timedelta(minutes=5)
        busy_cells = Pack.objects.filter(
            Q(delivery__exited_at__isnull=True) | Q(delivery__exited_at__gt=treshold)
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
            cell_code_min = agg_cells.aggregate(m=Min('code'))['m']
            cell_code_mean = (cell_code_max + cell_code_min) / 2

            def compare(cell):
                cell_code = cell.code
                if is_asc is False:
                    cell_code = cell_code_max - cell.code
                elif is_asc is None:
                    cell_code = abs(cell.code - cell_code_mean)
                return abs(cell.row.code - row_code_mean) * 100 + cell_code

            return sorted(cells, key=compare)[0]
        return None

    def barcode(self, pack):
        pilgrim = pack.delivery.pilgrim
        data = f'{pilgrim.get_full_name()}#{pilgrim.country}#{pack.delivery.hash_id}#{pilgrim.get_four_digit_phone()}'
        data = Encryption().cesar(data)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        path = f'{settings.TEMP_ROOT}/barcode/{datetime.now().strftime("%H:%M")}-{file_name}.jpg'
        img.save(path)
        return path

    def print(self, pack):
        badge_count = pack.bag_count + pack.pram_count + pack.suitcase_count
        ph = PrintHelper()
        pilgrim = pack.delivery.pilgrim
        entered_at = JalaliDatetime(pack.delivery.entered_at).strftime("%A %d %B %H:%M")
        barcode = self.barcode(pack)
        depository = pack.cell.row.cabinet.depository
        for idx in range(badge_count):
            html = render_to_string('badge.html', {
                'name': pilgrim.get_full_name(), 'index': idx + 1, 'count': badge_count,
                'country': pilgrim.country, 'phone': pilgrim.get_four_digit_phone(), 'entered_at': entered_at,
                'code': pack.cell.get_code(), 'barcode': barcode, 'depository_name': depository.name

            })
            ph.print(html)

        html = render_to_string('reciept.html', {
            'depository_name': depository.name, 'depository_address': depository.address,
            'social': settings.CONST_KEY_SOCIAL, 'phone': settings.CONST_KEY_PHONE,
            'notice': 'You have only got 24 hours for borrowing your packages', 'entered_at': entered_at,
            'barcode': barcode
        })
        ph.print(html, height=120)

    def report(self):
        total_count = Delivery.objects.count()
        distribution = {'total': total_count, }
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
