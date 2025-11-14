import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Program, TherapyOffering, Product, JournalPost, Booking, ContactMessage

app = FastAPI(title="Aham Eva API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"brand": "Aham Eva", "status": "ok"}


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
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Seed minimal content if empty (idempotent)
@app.post("/seed")
def seed_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    created = {"program": False, "therapy": False, "product": False, "journal": False}

    if db["program"].count_documents({"slug": "90-day-rebirth"}) == 0:
        program = Program(
            title="The 90-Day Rebirth",
            slug="90-day-rebirth",
            tagline="Reset. Rewire. Remember who you are.",
            description="A structured, compassionate 90-day journey combining psychology, breathwork, and contemplative practice.",
            duration_days=90,
            price_usd=499,
            modules=[{"day": 1, "title": "Arrival", "summary": "Breathe, land, and begin."}],
            featured=True,
        )
        create_document("program", program)
        created["program"] = True

    if db["therapyoffering"].count_documents({"slug": "integrative-therapy-60"}) == 0:
        therapy = TherapyOffering(
            title="Integrative Therapy (60 mins)",
            slug="integrative-therapy-60",
            description="Evidence-based therapy held with presence and care.",
            format="1:1",
            duration_minutes=60,
            price_usd=120,
        )
        create_document("therapyoffering", therapy)
        created["therapy"] = True

    if db["product"].count_documents({"slug": "morning-breath-audio"}) == 0:
        product = Product(
            title="Morning Breath Ritual (Audio)",
            slug="morning-breath-audio",
            description="A 12-minute guided breath sequence to begin clear and steady.",
            price_usd=9,
            kind="digital_audio",
        )
        create_document("product", product)
        created["product"] = True

    if db["journalpost"].count_documents({"slug": "on-wholeness"}) == 0:
        post = JournalPost(
            title="On Wholeness",
            slug="on-wholeness",
            excerpt="What returns when we stop trying to be more.",
            content_md="# On Wholeness\n\nIn the quiet, you are complete.",
        )
        create_document("journalpost", post)
        created["journal"] = True

    return {"seeded": created}


# Programs
@app.get("/programs")
def list_programs():
    docs = get_documents("program")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs


@app.get("/programs/{slug}")
def get_program(slug: str):
    doc = db["program"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Program not found")
    doc["_id"] = str(doc["_id"]) if "_id" in doc else None
    return doc


# Therapy
@app.get("/therapy")
def list_therapy():
    docs = get_documents("therapyoffering")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs


# Shop
@app.get("/shop")
def list_products():
    docs = get_documents("product")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs


# Journal
@app.get("/journal")
def list_posts():
    docs = get_documents("journalpost")
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs


# Booking + Contact
@app.post("/book")
def create_booking(payload: Booking):
    booking_id = create_document("booking", payload)
    return {"id": booking_id, "status": "scheduled"}


@app.post("/contact")
def create_message(payload: ContactMessage):
    msg_id = create_document("contactmessage", payload)
    return {"id": msg_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
