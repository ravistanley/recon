from weasyprint import HTML
from report.renderers.base import Renderer
from report.renderers.html import HTMLRenderer
from models.report import ReportData

class PDFRenderer(Renderer):
    async def render(self, report: ReportData) -> bytes:
        html_renderer = HTMLRenderer()
        html_string = await html_renderer.render(report)
        pdf = HTML(string=html_string).write_pdf()
        return pdf