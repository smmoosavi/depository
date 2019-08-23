import random
import string
import subprocess
from datetime import datetime

import pdfkit
from django.conf import settings


class PrintHelper:
    def generate_pdf(self, html,file_name=None):
        options = {
            # 'page-size': "A4",
            'page-width':'800',
            'page-height':'500',
            'margin-bottom': "0",
            'margin-top': '0',
            'margin-left': '0',
            'margin-right': '0',
        }
        if not file_name:
            file_name=''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            file_name=f'{datetime.now().strftime("%H:%M")}-{file_name}'
        config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        pdf = pdfkit.from_string(
            html, f'/home/vahid/Projects/depository/pdf/{file_name}.pdf', configuration=config, options=options)
        return pdf

    def print(self, html):
        pdf = self.generate_pdf(html)
        # subprocess.run(["ls", "-l"])
        # TODO
