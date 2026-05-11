from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from groq import Groq
import json
import os
import logging
from database import get_connection
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
model = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class MedicineRequest(BaseModel):
    medicine_name: str

def get_medicine_info_from_ai(medicine_name: str) -> dict:
    if not model:
        return {"name": medicine_name, "information": "AI service unavailable."}

    prompt = f"""You are a pharmacist AI. Provide information about: {medicine_name}

Respond ONLY as a valid JSON object:
{{
  "name": "Medicine generic name",
  "brand_names_india": ["Brand1", "Brand2"],
  "category": "Drug category",
  "uses": ["use 1", "use 2"],
  "dosage": "Typical adult dosage",
  "side_effects": ["side effect 1", "side effect 2"],
  "precautions": ["precaution 1"],
  "available_otc": true,
  "information": "2-3 sentence summary for the patient.",
  "disclaimer": "Always take medicines as prescribed by your doctor."
}}

Respond with ONLY the JSON, no other text."""

    try:
        response = model.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Medicine info error: {e}")
        return {"name": medicine_name, "information": f"Could not retrieve information for {medicine_name}."}

@router.post("/info")
def get_medicine_info(req: MedicineRequest, user_id: int = Depends(get_current_user)):
    result = get_medicine_info_from_ai(req.medicine_name)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO medicine_records (user_id, medicine_name, information) VALUES (?, ?, ?)",
            (user_id, req.medicine_name, json.dumps(result))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"DB error: {e}")
    finally:
        conn.close()
    return result

@router.get("/count")
def get_medicine_count(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as count FROM medicine_records WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return {"count": count["count"] if count else 0}

@router.get("/history")
def get_medicine_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM medicine_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]
