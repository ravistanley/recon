#!/usr/bin/env python3
import asyncio
import argparse
import sys
from core.orchestrator import Orchestrator
from report.renderers.html import HTMLRenderer
from report.renderers.markdown import MarkdownRenderer
from report.renderers.pdf import PDFRenderer
from config.settings import REPORT_DIR

async def main():
    parser = argparse.ArgumentParser(description="HOLLOW Recon Framework")
    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument("--format", choices=["html", "md", "pdf"], default="html")
    parser.add_argument("--skip-ping", action="store_true", help="Skip ICMP ping check")
    args = parser.parse_args()

    orch = Orchestrator(args.target)
    report = await orch.run(skip_ping=args.skip_ping)

    if report is None:
        print("[-] Recon aborted (target unreachable or no open ports).")
        return 1

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if args.format == "html":
        renderer = HTMLRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.html"
        out_path.write_text(content)
        print(f"[HOLLOW] HTML report saved: {out_path}")
    elif args.format == "md":
        renderer = MarkdownRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.md"
        out_path.write_text(content)
        print(f"[HOLLOW] Markdown report saved: {out_path}")
    elif args.format == "pdf":
        renderer = PDFRenderer()
        content = await renderer.render(report)
        out_path = REPORT_DIR / f"{args.target}_report.pdf"
        out_path.write_bytes(content)
        print(f"[HOLLOW] PDF report saved: {out_path}")

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))