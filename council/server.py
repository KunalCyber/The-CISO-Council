"""FastAPI server for The CISO Council War Room.

Serves the frontend and exposes the council engine as REST API endpoints.
Run with: python -m council serve
Or directly: uvicorn council.server:app --reload
"""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from council.config import load_config, log_key_status
from council.pdf_report import generate_pdf_report
from council.personas import list_personas
from council.report import load_latest_report, save_report
from council.session import CouncilSession

# ─── App Setup ───
# This server is designed for LOCAL USE ONLY.
# Do not expose it on a public interface or deploy it without authentication.

app = FastAPI(
    title="The CISO Council",
    description="War Room API — local use only",
    version="0.1.0",
)

# Restrict to localhost origins only. This tool is not designed for public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)

# Serve static files (the War Room UI)
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

PROJECT_ROOT = Path(__file__).parent.parent


# ─── Startup ───

@app.on_event("startup")
async def startup_event() -> None:
    """Log API key status on startup. Never prints key values."""
    log_key_status()


# ─── Request Models ───

class SessionRequest(BaseModel):
    """Request to run a council session.

    Supply either scenario_path (a path to a YAML file) or custom_text
    (free-form scenario description). custom_text takes precedence.
    """
    scenario_path: str | None = None
    members: list[str] | None = None
    custom_text: str | None = None


# ─── Routes ───

@app.get("/")
async def serve_frontend():
    """Serve the War Room UI."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(str(index_path))


@app.get("/api/personas")
async def get_personas():
    """Return all available council personas."""
    personas = list_personas()
    return {
        "personas": [
            {
                "id": p.id,
                "name": p.name,
                "title": p.title,
                "risk_appetite": p.risk_appetite.value,
                "org_context": {
                    "sector": p.org_context.sector,
                    "size": p.org_context.size,
                    "maturity": p.org_context.maturity,
                    "region": p.org_context.region,
                },
                "regulatory_lens": p.regulatory_lens,
                "decision_style": p.decision_style.value,
                "background": p.background,
            }
            for p in personas
        ]
    }


@app.get("/api/scenarios")
async def get_scenarios():
    """Return all available scenarios from the scenarios directory."""
    scenarios_dir = PROJECT_ROOT / "scenarios"
    scenarios = []

    for yaml_path in sorted(scenarios_dir.rglob("*.yaml")):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            rel_path = str(yaml_path.relative_to(PROJECT_ROOT))
            scenarios.append({
                "path": rel_path,
                "title": data.get("title", yaml_path.stem),
                "domain": data.get("domain", "unknown"),
            })
        except Exception:
            continue

    return {"scenarios": scenarios}


@app.post("/api/session/run")
async def run_session(request: SessionRequest):
    """Run a council session on the specified scenario.

    Loads the scenario, dispatches it to each configured council member,
    scores the responses, synthesises consensus/dissent analysis, and
    returns the full CouncilReport as JSON.
    """
    if not request.custom_text and not request.scenario_path:
        raise HTTPException(status_code=400, detail="Provide scenario_path or custom_text.")

    try:
        config = load_config()
        session = CouncilSession(config)

        if request.custom_text:
            from council.models import Scenario
            scenario = Scenario(
                title="Custom Scenario",
                domain="custom",
                context=request.custom_text,
                dilemma=request.custom_text,
            )
            report = await session.run(scenario=scenario, members=request.members)
        else:
            scenario_path = PROJECT_ROOT / request.scenario_path
            if not scenario_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario not found: {request.scenario_path}",
                )
            report = await session.run(
                scenario_path=scenario_path,
                members=request.members,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Session failed: {type(exc).__name__}: {exc}",
        )

    # Persist to outputs/ in background (non-blocking).
    try:
        output_dir = PROJECT_ROOT / config.output.directory
        save_report(report, output_dir=output_dir, fmt=config.output.format)
    except Exception:
        pass  # Saving is best-effort; never fail the API response over it.

    return report.model_dump(mode="json")


@app.get("/api/session/latest/export")
async def export_latest():
    """Generate and serve the most recent session report as a PDF download."""
    try:
        config = load_config()
        output_dir = PROJECT_ROOT / config.output.directory
        report_data = load_latest_report(output_dir=output_dir)
    except Exception:
        report_data = None

    if not report_data:
        return JSONResponse(
            content={"message": "No saved reports found in outputs/."},
            status_code=404,
        )

    try:
        pdf_bytes = generate_pdf_report(report_data)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {type(exc).__name__}: {exc}",
        )

    session_id = report_data.get("session_id", "report")
    filename = f"CISO_Council_Report_{session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "no-cache",
        },
    )


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "online", "version": "0.1.0"}
