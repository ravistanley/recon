from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from report.renderers.base import Renderer
from models.report import ReportData

class HTMLRenderer(Renderer):
    def __init__(self, template_dir: Path = Path("templates")):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def render(self, report: ReportData) -> str:
        template = self.env.get_template("report_template.html")
        return template.render(report=report)