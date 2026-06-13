from report.renderers.base import Renderer
from models.report import ReportData

class MarkdownRenderer(Renderer):
    async def render(self, report: ReportData) -> str:
        lines = []
        lines.append(f"# Recon Report: {report.target}")
        lines.append(f"**Timestamp:** {report.timestamp}")
        lines.append("\n## Services\n")
        for svc in report.services:
            lines.append(f"- Port {svc.port}: {svc.category.value} ({svc.product} {svc.version})")
        lines.append("\n## CVEs\n")
        for cve in report.cves:
            lines.append(f"- **{cve.id}** (CVSS {cve.cvss_score}) – {cve.description[:100]}")
        lines.append("\n## Plugin Outputs\n")
        for name, output in report.plugin_outputs.items():
            lines.append(f"\n### {name}\n```\n{output}\n```")
        return "\n".join(lines)