from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Store a reference to the running event loop for cross-thread SSE broadcasting."""
    from app.api.v1.stream import set_event_loop
    loop = asyncio.get_running_loop()
    set_event_loop(loop)

    # Ensure all DB tables exist (including new AuditLog)
    from app.database import engine, Base
    from app.models import audit_log  # noqa: ensure model is registered
    Base.metadata.create_all(bind=engine)
    print("[Sentinels] Database tables verified/created.")


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}


from app.api.v1 import inputs, tickets, reports, dashboards, auth, stream, audit

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(inputs.router, prefix="/api/v1/inputs", tags=["Inputs"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["Dashboards"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["Stream"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

