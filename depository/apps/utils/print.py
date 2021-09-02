import logging
import os
import random
import string
import subprocess
from datetime import datetime
from django.conf import settings

from weasyprint import HTML

logger = logging.getLogger(__name__)


class PrintHelper:
    def __init__(self, printer_id):
        self.printer_id = printer_id

    def generate_pdf(self, html, width=73, height=90):
        file_name = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=5))
        time_str = datetime.now().strftime("%H:%M")
        path = f"{settings.TEMP_ROOT}/pdf/{time_str}-{file_name}.pdf"
        HTML(string=html, base_url="file://").write_pdf(path)
        return path

    def print(self, pathes):
        try:
            subprocess.run(["lpr", "-P", f"depos-printer-{self.printer_id}", *pathes])
            # subprocess.run(["lpr", "-P", "OSCAR-POS88F-NET", *pathes])
            for path in pathes:
                os.remove(path)
            return True
        except Exception as e:
            logger.exception(e)
            return False
