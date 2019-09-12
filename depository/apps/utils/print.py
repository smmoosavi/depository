import os
import random
import string
import subprocess
from datetime import datetime

import pdfkit
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PrintHelper:
    def generate_pdf(self, html, width=73, height=90):
        options = {
            # 'page-size': "A4",
            'orientation': 'Portrait',
            'page-width': str(width),
            'page-height': str(height),
            'margin-bottom': "0",
            'margin-top': '0',
            'margin-left': '0',
            'margin-right': '0',
        }
        file_name = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=5))
        time_str = datetime.now().strftime("%H:%M")
        path = f"{settings.TEMP_ROOT}/pdf/{time_str}-{file_name}.pdf"
        config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        pdf = pdfkit.from_string(
            html, path, configuration=config, options=options)
        return path

    def print(self, pathes):
        try:
            subprocess.run(["lpr", "-P", "OSCAR-POS88F-USB", *pathes])
            for path in pathes:
                os.remove(path)
            return True
        except Exception as e:
            logger.exception(e)
            return False

