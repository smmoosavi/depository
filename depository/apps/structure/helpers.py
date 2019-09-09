from django.conf import settings
from django.template.loader import render_to_string

from depository.apps.utils.print import PrintHelper


class CodeHelper:
    def to_str(self, cabinet_code, row_code, cell_code):
        return ("{:0%s}" % settings.CABINET_DIGITS).format(cabinet_code) + \
               ("{:0%s}" % settings.ROW_DIGITS).format(row_code) + \
               ("{:0%s}" % settings.CELL_DIGITS).format(cell_code)

    def to_code(self, code):
        row, cell = None, None
        cabinet = int(code[:settings.CABINET_DIGITS])
        if len(code) > settings.CABINET_DIGITS:
            row = int(code[settings.CABINET_DIGITS:settings.CABINET_DIGITS + settings.ROW_DIGITS])
        if len(code) > (settings.CABINET_DIGITS + settings.ROW_DIGITS):
            cell = int(code[settings.CABINET_DIGITS + settings.ROW_DIGITS:])
        return cabinet, row, cell

    def print_cell_code(self, cell):
        return ("{:0%s}" % settings.ROW_DIGITS).format(cell.row.code) + \
               ("{:0%s}" % settings.CELL_DIGITS).format(cell.code)


class StructureHelper:
    def print(self, cabinet):
        ph = PrintHelper()
        ch = CodeHelper()
        for row in cabinet.rows.all():
            for cell in row.cells.all():
                html = render_to_string('number.html', {'number': cell.get_code()})
                ph.print(html)
