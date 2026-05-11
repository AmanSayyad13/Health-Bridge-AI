from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
import json
import os
import logging
from datetime import datetime
from database import get_connection
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
model = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class SymptomRequest(BaseModel):
    symptoms: str
    age: int = 25
    gender: str = "Male"
    duration: str = "1-3 days"
    existing_conditions: List[str] = []

def analyze_with_groq(req: SymptomRequest) -> dict:
    if not model:
        return {
            "analysis": "AI analysis unavailable. Please set GROQ_API_KEY.",
            "risk_level": "low",
            "see_doctor": False,
            "urgency": "Normal",
            "possible_conditions": []
        }

    prompt = f"""You are a medical AI assistant. Analyze the following symptoms and provide a structured medical assessment.

Patient Information:
- Age: {req.age}
- Gender: {req.gender}
- Symptom Duration: {req.duration}
- Existing Conditions: {', '.join(req.existing_conditions) if req.existing_conditions else 'None'}

Symptoms Described: {req.symptoms}

Respond ONLY as a valid JSON object with this exact structure:
{{
  "analysis": "Detailed 3-4 sentence medical analysis",
  "risk_level": "low",
  "see_doctor": false,
  "urgency": "Normal",
  "possible_conditions": [
    {{"name": "Condition Name", "probability": "High"}},
    {{"name": "Condition Name", "probability": "Medium"}}
  ],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "disclaimer": "Always consult a qualified medical professional."
}}

Risk level must be one of: low, medium, high
Urgency must be one of: Normal, Soon, Urgent, Emergency
Respond with ONLY the JSON, no other text."""

    try:
        response = model.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "analysis": "Analysis completed but response format error occurred.",
            "risk_level": "medium",
            "see_doctor": True,
            "urgency": "Soon",
            "possible_conditions": []
        }
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/analyze")
def analyze_symptoms(req: SymptomRequest, user_id: int = Depends(get_current_user)):
    result = analyze_with_groq(req)
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO symptom_records
            (user_id, symptoms, age, gender, duration, existing_conditions,
             analysis, risk_level, see_doctor, urgency, possible_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, req.symptoms, req.age, req.gender, req.duration,
            json.dumps(req.existing_conditions),
            result.get("analysis", ""),
            result.get("risk_level", "low"),
            result.get("see_doctor", False),
            result.get("urgency", "Normal"),
            json.dumps(result.get("possible_conditions", []))
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"DB error: {e}")
    finally:
        conn.close()
    return result

@router.get("/history")
def get_symptom_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM symptom_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]
