import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import EnergyProduct, ImpactStory, Inquiry, Office

app = FastAPI(title="Clean Energy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "clean-energy-backend"}

# Health and database test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            # Try list collections
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "❌ Database not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    # Environment flags
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ------ Content Endpoints ------

@app.get("/api/solutions", response_model=List[EnergyProduct])
def list_solutions(sector: Optional[str] = None, featured: Optional[bool] = None):
    """List energy solutions, optionally filter by sector or featured."""
    if db is None:
        # Return a few defaults for initial UX even without DB
        defaults = [
            EnergyProduct(name="Solar Inverters", sector="solar", summary="High-efficiency PV inverters for utility and C&I.", specs=["98.6% max efficiency", "Grid support"], image=None, featured=True),
            EnergyProduct(name="Wind Drive Systems", sector="wind", summary="Reliable drivetrain and control systems for wind turbines.", specs=["Low maintenance", "High uptime"], image=None, featured=True),
            EnergyProduct(name="Battery Energy Storage", sector="storage", summary="Modular, safe, and scalable storage systems.", specs=["LFP chemistry", "Liquid cooling"], image=None, featured=True),
        ]
        return defaults

    filt = {}
    if sector:
        filt["sector"] = sector
    if featured is not None:
        filt["featured"] = featured
    docs = get_documents("energyproduct", filt)
    return [EnergyProduct(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

@app.get("/api/stories", response_model=List[ImpactStory])
def list_stories(limit: int = 6):
    if db is None:
        return [
            ImpactStory(title="200 MW Solar + Storage in MENA", location="UAE", sector="solar", summary="Hybrid system powering 150k homes while avoiding 300k tons CO2 annually.", media_url=None, partner="Masdar"),
            ImpactStory(title="Offshore Wind Integration", location="North Sea", sector="wind", summary="Advanced grid-forming inverters stabilize offshore wind farms.", media_url=None, partner=""),
        ]
    docs = get_documents("impactstory", {}, limit=limit)
    return [ImpactStory(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

class InquiryResponse(BaseModel):
    ok: bool
    message: str

@app.post("/api/inquiry", response_model=InquiryResponse)
def submit_inquiry(payload: Inquiry):
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent required for storing contact info.")
    if db is not None:
        try:
            create_document("inquiry", payload)
        except Exception as e:
            # Even if DB write fails, acknowledge receipt
            return InquiryResponse(ok=False, message=f"Received but DB error: {str(e)[:80]}")
    return InquiryResponse(ok=True, message="Thank you. Our team will contact you shortly.")

@app.get("/api/offices", response_model=List[Office])
def list_offices():
    if db is None:
        return [
            Office(region="North America", city="San Francisco", email="na@cleantech.example"),
            Office(region="EMEA", city="Munich", email="emea@cleantech.example"),
            Office(region="APAC", city="Singapore", email="apac@cleantech.example"),
        ]
    docs = get_documents("office")
    return [Office(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
