from fastapi import APIRouter, Depends
from database import get_connection
from routers.auth import get_current_admin
import json

router = APIRouter()

@router.get("/stats")
def get_stats(admin_id: int = Depends(get_current_admin)):
    conn = get_connection()
    total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
    total_symptoms = conn.execute("SELECT COUNT(*) as count FROM symptom_records").fetchone()["count"]
    total_medicines = conn.execute("SELECT COUNT(*) as count FROM medicine_records").fetchone()["count"]
    high_risk = conn.execute("SELECT COUNT(*) as count FROM symptom_records WHERE risk_level = 'high'").fetchone()["count"]
    conn.close()
    return {
        "total_users": total_users,
        "total_symptom_checks": total_symptoms,
        "total_medicine_lookups": total_medicines,
        "high_risk_cases": high_risk
    }

@router.get("/users")
def get_all_users(admin_id: int = Depends(get_current_admin)):
    conn = get_connection()
    users = conn.execute("""
        SELECT u.id, u.name, u.email, u.age, u.created_at,
        COUNT(DISTINCT s.id) as symptom_checks,
        COUNT(DISTINCT m.id) as medicine_lookups
        FROM users u
        LEFT JOIN symptom_records s ON u.id = s.user_id
        LEFT JOIN medicine_records m ON u.id = m.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(u) for u in users]

@router.get("/users/{user_id}/activity")
def get_user_activity(user_id: int, admin_id: int = Depends(get_current_admin)):
    conn = get_connection()
    user = conn.execute("SELECT id, name, email, age, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    symptoms = conn.execute("""
        SELECT symptoms, risk_level, see_doctor, urgency, analysis, created_at
        FROM symptom_records WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 20
    """, (user_id,)).fetchall()
    medicines = conn.execute("""
        SELECT medicine_name, created_at FROM medicine_records
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 20
    """, (user_id,)).fetchall()
    conn.close()
    return {
        "user": dict(user) if user else {},
        "symptom_checks": [dict(s) for s in symptoms],
        "medicine_lookups": [dict(m) for m in medicines]
    }

@router.get("/symptoms/all")
def get_all_symptoms(admin_id: int = Depends(get_current_admin)):
    conn = get_connection()
    records = conn.execute("""
        SELECT s.id, u.name, u.email, s.symptoms, s.risk_level,
        s.see_doctor, s.urgency, s.created_at
        FROM symptom_records s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC LIMIT 50
    """).fetchall()
    conn.close()
    return [dict(r) for r in records]
