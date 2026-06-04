from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.analytics import compute_analytics
from app.database import clear_places, get_places, init_db, save_places
from app.scraper import scrape_google_maps

BASE_DIR = Path(__file__).parent.parent

app = FastAPI(title="Google Maps Lead Intelligence")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

_status: dict = {"running": False, "message": "Ready"}


@app.on_event("startup")
def startup():
    init_db()


def _run_scraping(query: str, industry: str, max_results: int):
    global _status
    _status = {"running": True, "message": f"Scraping '{query}' ({max_results} max)…"}
    try:
        places = scrape_google_maps(query, industry, max_results)
        save_places(places)
        _status = {
            "running": False,
            "message": f"✓ {len(places)} établissements collectés pour '{query}'",
        }
    except Exception as exc:
        _status = {"running": False, "message": f"Erreur : {exc}"}


@app.get("/")
def home(request: Request):
    places = get_places()
    analytics = compute_analytics(places)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "places": places,
            "analytics": analytics,
            "status": _status,
        },
    )


@app.post("/run-scraping")
def start_scraping(
    background_tasks: BackgroundTasks,
    query: str = Form(...),
    industry: str = Form(...),
    max_results: int = Form(10),
):
    if not _status["running"]:
        background_tasks.add_task(_run_scraping, query, industry, max_results)
    return RedirectResponse(url="/", status_code=303)


@app.post("/clear")
def clear(request: Request):
    clear_places()
    return RedirectResponse(url="/", status_code=303)
