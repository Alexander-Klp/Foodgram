import os

from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_shopping_cart_pdf(ingredients, filename='shopping_cart.pdf'):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    font_path = os.path.join(
        os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf'
    )
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    page_number = 1

    def draw_header_footer():
        """
        Отрисовывает заголовок и номер страницы.
        """
        p.setFont("DejaVuSans", 20)
        p.drawString(230, height - 90, 'Список покупок')
        p.setFont("DejaVuSans", 16)
        p.drawString(100, height - 150, 'Ингредиенты:')
        p.setFont("DejaVuSans", 10)
        p.drawString(width - 100, 40, f"Страница {page_number}")

    draw_header_footer()

    p.setFont("DejaVuSans", 12)
    y_position = height - 180
    line_height = 20

    for ingredient in ingredients:
        text = (
            f"{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}): "
            f"{ingredient['total_amount']}"
        )

        if y_position < line_height + 40:
            p.showPage()
            page_number += 1
            y_position = height - 60
            draw_header_footer()
            y_position = height - 180
            p.setFont("DejaVuSans", 12)

        p.drawString(100, y_position, text)
        y_position -= line_height

    p.showPage()
    p.save()

    return response
