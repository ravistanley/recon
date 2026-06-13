#!/usr/bin/env python3
import asyncio
import argparse
from core.orchestrator import Orchestrator
from report.renderers.html import HTMLRenderer
from report.renderers.markdown import MarkdownRenderer
from report.renderers.pdf import PDFRenderer
from config.settings import REPORT_DIR

async def main():
    parser = argparse.ArgumentParser(description="HOLLOW Recon Framework")
    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument("--format", choices=["html", "md", "pdf"], default="html")
    args = parser.parse_args()

    orch = Orchestrator(args.target)
    report = await orch.run()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if args.format == "html":
        renderer = HTMLRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.html"
        out_path.write_text(content)
    elif args.format == "md":
        renderer = MarkdownRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.md"
        out_path.write_text(content)
    elif args.format == "pdf":
        renderer = PDFRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.pdf"
        out_path.write_bytes(content)

    print(f"[HOLLOW] Report saved: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())