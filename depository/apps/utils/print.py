import os
import random
import string
import subprocess
from datetime import datetime

import pdfkit
from django.conf import settings


class PrintHelper:
    def generate_pdf(self, html, width=75, height=50):
        options = {
            # 'page-size': "A4",
            'page-width': str(width),
            'page-height': str(height),
            'margin-bottom': "0",
            'margin-top': '0',
            'margin-left': '0',
            'margin-right': '0',
        }
        file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        path = f'{settings.TEMP_ROOT}/pdf/{datetime.now().strftime("%H:%M")}-{file_name}.pdf'
        config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        pdf = pdfkit.from_string(
            html, path, configuration=config, options=options)
        return path

    def print(self, html, width=75, height=50):
        path = self.generate_pdf(html, width, height)
        # subprocess.run(["ls", "-l"])
        # os.remove(path) ?
        # TODO:
