import locale

from django.conf import settings
from django.template.loader import render_to_string

from depository.apps.structure.models import Constant, Cell, Row
from depository.apps.utils.print import PrintHelper


class CodeHelper:
    def to_str(self, cabinet_code, row_code, cell_code):
        return ("%s" % cabinet_code) + \
               ("{:0%s}" % settings.ROW_DIGITS).format(row_code) + \
               ("%s" % cell_code)

    def to_code(self, code):
        row, cell = None, None
        cabinet = code[:settings.CABINET_DIGITS]
        if len(code) > settings.CABINET_DIGITS:
            row = int(code[settings.CABINET_DIGITS:settings.CABINET_DIGITS + settings.ROW_DIGITS])
        if len(code) > (settings.CABINET_DIGITS + settings.ROW_DIGITS):
            cell = int(code[settings.CABINET_DIGITS + settings.ROW_DIGITS:])
        return cabinet, row, cell


class StructureHelper:
    def print(self, cabinet):
        ph = PrintHelper()
        pathes = []
        for row in cabinet.rows.all():
            for cell in row.cells.all():
                code = cell.get_code()
                alphabet = code[:settings.CABINET_DIGITS]
                number = code[settings.CABINET_DIGITS:]
                html = render_to_string('number.html',
                                        {'number': number, 'alphabet': alphabet, 'BASE_DIR': settings.BASE_DIR})
                pathes.append(ph.generate_pdf(html))
        ph.print(pathes)

    def extend(self, cabinet, data):
        print(data)
        if data['num_of_cols']:
            cell = Cell.objects.filter(row__cabinet=cabinet).order_by('-code').first()
            first_index = 0
            if cell:
                first_index = cell.code + 1
            for row in cabinet.rows:
                size = row.cells[0].size
                for index in range(data['num_of_cols']):
                    Cell.objects.create(row=row, code=index + first_index, size=size)
        if data['num_of_rows']:
            cells_count = cabinet.rows[0].cells.count()
            first_index = 0
            one_row = cabinet.rows.order_by('-code').first()
            if one_row:
                first_index = one_row.code + 1
            for index in range(data['num_of_rows']):
                row = Row.objects.create(cabinet=cabinet, code=index + first_index)
                for i in range(cells_count):
                    Cell.objects.create(row=row, code=i)
        cabinet.refresh_from_db()
        return cabinet


class CellHelper:
    def print(self, cell):
        html = render_to_string('number.html', {'number': cell.get_code(), 'BASE_DIR': settings.BASE_DIR})
        ph = PrintHelper()
        ph.print([ph.generate_pdf(html)])


class ConstantHelper:
    def get(self, key, default=None):
        try:
            return Constant.objects.get(key=key).value
        except Constant.DoesNotExist:
            if default:
                return default
            else:
                return key

    def get_notice(self, country):
        return self.get(
            settings.CONST_KEY_NOTICE % settings.LANG_DICT.get(country.lower(), {}).get('languages', ['en'])[0],
            default='You have only got 24 hours for borrowing your packages'
        )

    def set_locale(self, country):
        country_brief_name = settings.LANG_DICT.get(country.lower(), {}).get('brief_name', 'US')
        locale_name = settings.LANG_DICT.get(country.lower(), {}).get('languages', ['en'])[0]
        if country_brief_name:
            locale_name = f"{locale_name}_{country_brief_name}"
        locale.setlocale(locale.LC_ALL, locale_name)
