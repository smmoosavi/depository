import pdfkit
from django.conf import settings


class PrintHelper:
    def generate_pdf(self, html):
        options = {
            'page-size': "A4",
            'margin-bottom': "0",
            'margin-top': '5',
            'margin-left': '0',
            'margin-right': '0',
        }
        config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        pdf = pdfkit.from_string(
            html, False, configuration=config, options=options)
        return pdf

    def print(self, html):
        pdf = self.generate_pdf(html)
        # TODO
