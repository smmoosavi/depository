from django.conf import settings


class CodeHelper:

    def to_str(self, cabinet, row, cell):
        return ("{:%sf}" % settings.CABINET_DIGITS).format(cabinet) + \
               ("{:%sf}" % settings.ROW_DIGITS).format(row) + \
               ("{:%sf}" % settings.CELL_DIGITS).format(cell)

    def to_code(self, code):
        row, cell = None, None
        cabinet = int(code[:settings.CABINET_DIGITS])
        if len(code) > settings.CABINET_DIGITS:
            row = int(code[settings.CABINET_DIGITS:settings.CABINET_DIGITS + settings.ROW_DIGITS])
        if len(code) > (settings.CABINET_DIGITS + settings.ROW_DIGITS):
            cell = int(code[settings.CABINET_DIGITS + settings.ROW_DIGITS:])
        return cabinet, row, cell
