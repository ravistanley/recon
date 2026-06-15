from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from report.renderers.base import Renderer
from models.report import ReportData
import json

class HTMLRenderer(Renderer):
    def __init__(self, template_dir: Path = Path("templates")):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def render(self, report: ReportData) -> str:
        template = self.env.get_template("report_template.html")
        pretty_plugins = {}
        for name, output in report.plugin_outputs.items():
            # keep gobuster and nse as dicts for iteration
            if name in ('nse', 'gobuster'):
                pretty_plugins[name] = output
            elif isinstance(output, dict):
                pretty_plugins[name] = json.dumps(output, indent=2)
            else:
                pretty_plugins[name] = str(output)
        return template.render(report=report, plugin_outputs=pretty_plugins)