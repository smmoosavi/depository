import base64
import logging
import os
import random
import string
from datetime import datetime
from datetime import timedelta

import qrcode
from django.conf import settings
from django.db.models import Max, Min, Count, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from khayyam.jalali_datetime import JalaliDatetime

from depository.apps.reception.models import Pack, Delivery
from depository.apps.structure.helpers import ConstantHelper
from depository.apps.structure.models import Cell, Cabinet
from depository.apps.utils.excel import ExcelUtil
from depository.apps.utils.print import PrintHelper

logger = logging.getLogger(__name__)


class ReceptionHelper:
    def assign_cell(self, size):
        assert size in [Cell.SIZE_SMALL, Cell.SIZE_LARGE]
        treshold = timezone.now() - timezone.timedelta(minutes=settings.REVERT_THRESHOLD)
        busy_cells = Pack.objects.filter(
            Q(delivery__exited_at__isnull=True) | Q(delivery__exited_at__gt=treshold)
        ).values_list('cell', flat=True)
        for cabinet in Cabinet.objects.order_by('order'):
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

            cells = sorted(cells, key=compare)
            logger.info(
                f"{row_code_max} {row_code_min} {row_code_mean} {cell_code_max} {cell_code_min} {cell_code_mean}"
            )
            logger.info(f"empty cells: {cells}")
            logger.info(f"busy cells: {busy_cells}")
            logger.info(f"return best cell {cells[0]}")
            return cells[0]
        first_cell = Cell.objects \
            .filter(is_healthy=True, size=size) \
            .exclude(pk__in=busy_cells) \
            .order_by('row__cabinet__order').first()
        if not first_cell:
            logger.info(f"no free cell")
            return None
        logger.info(f"return first cell {first_cell}")
        return first_cell

    def barcode(self, pack):
        pilgrim = pack.delivery.pilgrim
        data = f'{pilgrim.get_full_name()}#{pilgrim.country}#{pack.delivery.hash_id}#' \
               f'{pilgrim.get_four_digit_phone()}#{pack.cell.get_code()}'
        data = base64.b64encode(force_bytes(data)).decode("utf-8")
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
        pilgrim = pack.delivery.pilgrim
        ch = ConstantHelper(country=pilgrim.country)
        entered_at_jalali = JalaliDatetime(timezone.localtime(pack.delivery.entered_at)).strftime("%A %d %B %H:%M")
        barcode = self.barcode(pack)
        depository = pack.cell.row.cabinet.depository
        ph = PrintHelper(depository.printer_id)
        pathes = []
        for idx in range(badge_count):
            html = render_to_string('badge.html', {
                'name': pilgrim.get_full_name(), 'index': idx + 1, 'count': badge_count,
                'country': pilgrim.country, 'phone': pilgrim.get_four_digit_phone(), 'entered_at': entered_at_jalali,
                'code': pack.cell.get_printable_code(), 'barcode': barcode,
                'depository_name': ch.get_depository_name(depository), 'taker': pack.delivery.taker.get_full_name(),
                "BASE_DIR": settings.BASE_DIR
            }, )
            pathes.append(ph.generate_pdf(html))
        ####################################### Print Receipt #########################################
        data = {
            'name': pilgrim.get_full_name(), 'depository_name': depository.name,
            'depository_address': ch.get_depository_address(depository),
            'social': ch.get(settings.CONST_KEY_SOCIAL), 'phone': ch.get(settings.CONST_KEY_PHONE),
            'notice': ch.get_notice(),
            'barcode': barcode, "BASE_DIR": settings.BASE_DIR
        }
        if pilgrim.is_iranian():
            data.update({
                'entered_at': JalaliDatetime(timezone.localtime(pack.delivery.entered_at)).strftime("%A %d %B %H:%M"),
                'font': 'IranSans'
            })

        else:
            data.update({
                'entered_at': timezone.localtime(pack.delivery.entered_at).strftime("%A %d %B %H:%M:%S"),
                'font': "Calibri Light"

            })
        html = render_to_string('reciept.html', data)
        pathes.append(ph.generate_pdf(html, height=120))

        ph.print(pathes)
        os.remove(barcode)

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

    def admin_report(self):
        total_cabinets = Cabinet.objects.count()
        total_cells = Cell.objects.count()
        busy_cells = Pack.objects.filter(cell__is_healthy=True).filter(
            Q(delivery__exited_at__isnull=True) | Q(delivery__exited_at__gt=timezone.now())
        ).count()
        empty_cells = Cell.objects.filter(is_healthy=True).count() - busy_cells
        total_deliveries = Delivery.objects.count()
        return {
            'total_cabinets': total_cabinets, 'total_cells': total_cells,
            'empty_cells': empty_cells, 'total_deliveries': total_deliveries
        }

    def export_data(self, **kwargs):
        data = []
        for delivery in Delivery.objects.filter(**kwargs).all():
            packs = delivery.packs.all()
            data.append({
                'enter': JalaliDatetime(delivery.entered_at).strftime("%Y/%m/%d %H:%M") if delivery.entered_at else '-',
                'exit': JalaliDatetime(delivery.exited_at).strftime("%Y/%m/%d %H:%M") if delivery.exited_at else '-',
                'taker': delivery.taker.get_full_name() if delivery.taker else '-',
                'giver': delivery.giver.get_full_name() if delivery.giver else '-',
                'first_name': delivery.pilgrim.first_name,
                'last_name': delivery.pilgrim.last_name,
                'phone': delivery.pilgrim.phone,
                'country': delivery.pilgrim.country,
                'bag': sum([item.bag_count for item in packs]),
                'suitcase_count': sum([item.suitcase_count for item in packs]),
                'pram_count': sum([item.pram_count for item in packs])
            })
        if data:
            header = list(data[0].keys())
            return ExcelUtil().export_file(header, data)
