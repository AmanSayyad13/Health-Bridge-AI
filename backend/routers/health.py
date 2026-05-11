from fastapi import APIRouter, Depends
from database import get_connection
from routers.auth import get_current_user
import json

router = APIRouter()

@router.get("/history")
def get_full_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    records = conn.execute(
        """SELECT id, symptoms, risk_level, see_doctor, urgency, analysis, created_at
           FROM symptom_records WHERE user_id = ?
           ORDER BY created_at DESC LIMIT 50""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]

@router.get("/summary")
def get_health_summary(user_id: int = Depends(get_current_user)):
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) as count FROM symptom_records WHERE user_id = ?", (user_id,)
    ).fetchone()["count"]

    high_risk = conn.execute(
        "SELECT COUNT(*) as count FROM symptom_records WHERE user_id = ? AND risk_level = 'high'", (user_id,)
    ).fetchone()["count"]

    medicines = conn.execute(
        "SELECT COUNT(*) as count FROM medicine_records WHERE user_id = ?", (user_id,)
    ).fetchone()["count"]

    conn.close()
    return {
        "total_checks": total,
        "high_risk_count": high_risk,
        "medicines_looked_up": medicines
    }
