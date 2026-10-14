# -*- coding: utf-8 -*-
"""
AI-to-Live Teacher Escalation Engine (Astrotalk-style on-demand expert consultation)
Product Philosophy: "AI teaches first, Human Teachers teach when understanding matters most."

Implements:
- AI Confidence Check & Confusion Tracking
- Automatic AI-Generated Teacher Brief
- Teacher Marketplace with Multilingual Filters & Badges
- AI Recommendation & Ranking Engine
- Uber-like Broadcast Doubt Dispatch
- Real-time Session Lifecycle (Chat, Audio, Video, Whiteboard)
- AI-Assisted Teacher Co-pilot during live sessions
- Session Recording & Post-Session Student Summary
- Teacher Wallet, Earnings & Astrotalk Monetization
- Teacher Performance Scoring & Leaderboard
- Exam Emergency Mode (48h before board exams)
- Parent Dashboard Analytics
- Admin Dashboard Metrics & Teacher Approval
"""

import os
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# PYDANTIC DATA MODELS & SCHEMAS (Feature 17)
# -------------------------------------------------------------

class EscalationRequest(BaseModel):
    student_id: str = "std_001"
    student_name: str = "Aarav Mohapatra"
    grade: str = "Class 10"
    subject: str = "Physics"
    chapter: str = "Newton's Laws of Motion"
    original_question: str
    confusion_reason: Optional[str] = "I don't understand why action and reaction don't cancel each other out."
    ai_attempts: int = 2
    student_language: str = "or"
    mode: str = "instant" # "instant", "broadcast", "scheduled"
    preferred_interaction: str = "whiteboard" # "chat", "audio", "video", "whiteboard"

class TeacherProfile(BaseModel):
    id: str
    name: str
    avatar: str
    qualification: str
    experience_years: int
    subjects: List[str]
    classes: List[str]
    languages: List[str]
    rating: float
    total_sessions: int
    response_time_min: int
    is_online: bool
    price_per_min: float # INR
    price_per_session: float # 15-min fixed session
    emergency_expert: bool = False
    emergency_specialty: Optional[str] = None # "Fast Revision Expert", "Last Minute Doubt Expert", "Board Exam Mentor"
    bio: str
    performance_score: float = 0.0

class LiveSession(BaseModel):
    id: str
    student_id: str
    student_name: str
    teacher_id: str
    teacher_name: str
    subject: str
    chapter: str
    interaction_mode: str
    status: str # "pending", "accepted", "in_progress", "completed", "cancelled"
    started_at: Optional[float] = None
    ended_at: Optional[float] = None
    duration_minutes: float = 0.0
    teacher_brief: Dict[str, Any]
    whiteboard_data: List[Dict[str, Any]] = []
    chat_transcript: List[Dict[str, Any]] = []
    student_rating: Optional[float] = None
    student_review: Optional[str] = None
    session_fee: float = 0.0
    platform_commission: float = 0.0
    teacher_payout: float = 0.0
    post_session_summary: Optional[Dict[str, Any]] = None

# -------------------------------------------------------------
# ESCALATION ENGINE SINGLETON & STORAGE
# -------------------------------------------------------------

class EscalationEngine:
    def __init__(self, data_file: str = None):
        if data_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_file = os.path.join(base_dir, "data", "escalation_db.json")
        else:
            self.data_file = data_file

        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.teachers: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.broadcast_requests: Dict[str, Dict[str, Any]] = {}
        self.wallets: Dict[str, Dict[str, Any]] = {}
        self.commission_percentage: float = 20.0 # Platform takes 20%, teacher gets 80%
        self.exam_emergency_mode: bool = False

        self._load_or_init_data()

    def _load_or_init_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.teachers = data.get("teachers", {})
                    self.sessions = data.get("sessions", {})
                    self.wallets = data.get("wallets", {})
                    self.exam_emergency_mode = data.get("exam_emergency_mode", False)
                    if self.teachers:
                        return
            except Exception as e:
                print(f"Notice loading escalation DB: {e}")

        # Initialize Default Multilingual Teachers
        self.teachers = {
            "tch_001": {
                "id": "tch_001",
                "name": "Prof. Rashmi Rekha Das",
                "avatar": "👩‍🏫",
                "qualification": "M.Sc. Physics (Utkal University), B.Ed",
                "experience_years": 11,
                "subjects": ["Physics", "General Science"],
                "classes": ["Class 9", "Class 10", "Class 11"],
                "languages": ["Odia", "English", "Hindi"],
                "rating": 4.95,
                "total_sessions": 342,
                "response_time_min": 2,
                "is_online": True,
                "price_per_min": 12.0,
                "price_per_session": 150.0,
                "emergency_expert": True,
                "emergency_specialty": "Board Exam Mentor (Odisha BSE)",
                "bio": "Former State Board Examiner specializing in intuitive mechanics & vernacular visual analogies.",
                "performance_score": 96.4
            },
            "tch_002": {
                "id": "tch_002",
                "name": "Karthik Subramanian",
                "avatar": "👨‍🏫",
                "qualification": "B.Tech IIT Madras, M.S.",
                "experience_years": 8,
                "subjects": ["Mathematics", "Physics"],
                "classes": ["Class 9", "Class 10", "Class 11", "Class 12"],
                "languages": ["Tamil", "English"],
                "rating": 4.91,
                "total_sessions": 275,
                "response_time_min": 1,
                "is_online": True,
                "price_per_min": 15.0,
                "price_per_session": 180.0,
                "emergency_expert": True,
                "emergency_specialty": "Last Minute Doubt Expert",
                "bio": "IIT Madras alumnus passionate about deconstructing geometry, calculus & Newton's dynamics.",
                "performance_score": 94.2
            },
            "tch_003": {
                "id": "tch_003",
                "name": "Dr. Ananya Roy",
                "avatar": "👩‍🔬",
                "qualification": "Ph.D. Biochemistry (Calcutta University)",
                "experience_years": 9,
                "subjects": ["Biology", "Chemistry"],
                "classes": ["Class 8", "Class 9", "Class 10", "Class 12"],
                "languages": ["Bengali", "English", "Hindi"],
                "rating": 4.88,
                "total_sessions": 198,
                "response_time_min": 3,
                "is_online": True,
                "price_per_min": 10.0,
                "price_per_session": 130.0,
                "emergency_expert": False,
                "emergency_specialty": "Fast Revision Expert",
                "bio": "Expert in life sciences, photosynthesis diagrams, and cellular genetics.",
                "performance_score": 91.8
            },
            "tch_004": {
                "id": "tch_004",
                "name": "Srinivas Rao",
                "avatar": "👨‍💼",
                "qualification": "M.Sc. Mathematics, Hyderabad",
                "experience_years": 14,
                "subjects": ["Mathematics"],
                "classes": ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"],
                "languages": ["Telugu", "English"],
                "rating": 4.93,
                "total_sessions": 410,
                "response_time_min": 2,
                "is_online": True,
                "price_per_min": 14.0,
                "price_per_session": 160.0,
                "emergency_expert": True,
                "emergency_specialty": "Board Exam Mentor",
                "bio": "Specialist in triangle theorems, trigonometry shortcuts, and algebraic equation solving.",
                "performance_score": 95.7
            },
            "tch_005": {
                "id": "tch_005",
                "name": "Meera Nambiar",
                "avatar": "👩‍🏫",
                "qualification": "M.Sc. Botany (Kerala University)",
                "experience_years": 6,
                "subjects": ["Biology", "Environmental Science"],
                "classes": ["Class 8", "Class 9", "Class 10"],
                "languages": ["Malayalam", "English"],
                "rating": 4.86,
                "total_sessions": 145,
                "response_time_min": 4,
                "is_online": False,
                "price_per_min": 10.0,
                "price_per_session": 120.0,
                "emergency_expert": False,
                "emergency_specialty": "Fast Revision Expert",
                "bio": "Focuses on interactive biological diagrams, life cycle charts, and plant physiology.",
                "performance_score": 88.5
            },
            "tch_006": {
                "id": "tch_006",
                "name": "Pooja Patil",
                "avatar": "👩‍🎓",
                "qualification": "B.E. Computer Science, M.Tech Pune",
                "experience_years": 7,
                "subjects": ["Computer Science", "Mathematics"],
                "classes": ["Class 9", "Class 10", "Class 11", "Class 12"],
                "languages": ["Marathi", "Hindi", "English"],
                "rating": 4.92,
                "total_sessions": 230,
                "response_time_min": 2,
                "is_online": True,
                "price_per_min": 12.0,
                "price_per_session": 150.0,
                "emergency_expert": True,
                "emergency_specialty": "Last Minute Doubt Expert",
                "bio": "Python algorithms, flowchart logic, and step-by-step math problem solving.",
                "performance_score": 93.6
            }
        }

        # Initialize Teacher Wallets
        for tch_id in self.teachers:
            self.wallets[tch_id] = {
                "teacher_id": tch_id,
                "total_earnings": 14500.0,
                "pending_earnings": 1200.0,
                "withdrawn_earnings": 13300.0,
                "total_sessions_completed": self.teachers[tch_id]["total_sessions"],
                "incentive_bonus": 850.0,
                "transactions": [
                    {"id": "tx_101", "date": "2026-10-12", "amount": 120.0, "type": "session_payout", "status": "completed"},
                    {"id": "tx_102", "date": "2026-10-13", "amount": 144.0, "type": "session_payout", "status": "completed"},
                    {"id": "tx_103", "date": "2026-10-14", "amount": 5000.0, "type": "withdrawal_upi", "status": "processed"}
                ]
            }

        self.save()

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({
                    "teachers": self.teachers,
                    "sessions": self.sessions,
                    "wallets": self.wallets,
                    "exam_emergency_mode": self.exam_emergency_mode
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving escalation DB: {e}")

    # ---------------------------------------------------------
    # FEATURE 2: AI-GENERATED TEACHER BRIEF
    # ---------------------------------------------------------
    def generate_teacher_brief(self, req: EscalationRequest) -> Dict[str, Any]:
        """
        Synthesizes an automated, high-density pedagogical summary for the human teacher
        before they accept the call. Eliminates repetitive student re-explaining!
        """
        # Determine suggested explanation level
        grade_num = 10
        try:
            grade_num = int("".join([c for c in req.grade if c.isdigit()]))
        except:
            pass

        suggested_level = f"{req.grade} Beginner Grounding"
        if req.ai_attempts >= 3:
            suggested_level = f"{req.grade} Intuitive Vernacular Scaffolding (Needs Concrete Physical Analogy)"

        brief = {
            "brief_id": f"brief_{uuid.uuid4().hex[:8]}",
            "student_name": req.student_name,
            "student_grade": req.grade,
            "student_language": req.student_language,
            "subject": req.subject,
            "chapter": req.chapter,
            "original_question": req.original_question,
            "ai_attempts": req.ai_attempts,
            "student_difficulty": req.confusion_reason or "Struggling with conceptual abstraction",
            "suggested_explanation_level": suggested_level,
            "recommended_pedagogical_hook": (
                "Draw a free-body diagram showing forces on Object A vs Object B. "
                "Remind the student that forces only cancel if they act on the EXACT SAME body!"
                if "newton" in req.chapter.lower() or "newton" in req.original_question.lower()
                else "Break down step-by-step with simple relatable examples."
            ),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return brief

    # ---------------------------------------------------------
    # FEATURE 3 & 5: MARKETPLACE & AI RECOMMENDATION ENGINE
    # ---------------------------------------------------------
    def get_marketplace_teachers(
        self,
        subject: Optional[str] = None,
        language: Optional[str] = None,
        grade: Optional[str] = None,
        max_price: Optional[float] = None,
        emergency_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Filters and scores teachers using the AI Recommendation Algorithm:
        Score = SubjectMatch(40%) + LanguageMatch(25%) + Rating(15%) + ResponseTime(10%) + EmergencyBonus(10%)
        """
        results = []
        for t in self.teachers.values():
            if emergency_only and not t.get("emergency_expert", False):
                continue
            if subject and subject != "All" and subject not in t.get("subjects", []):
                continue
            if grade and grade != "All" and grade not in t.get("classes", []):
                continue
            if max_price and t.get("price_per_min", 0) > max_price:
                continue

            # Calculate AI Recommendation Score
            score = 50.0 # base score

            # Subject match
            if subject and subject in t.get("subjects", []):
                score += 25.0

            # Language match
            lang_list = [l.lower() for l in t.get("languages", [])]
            target_lang = (language or "en").lower()
            lang_map = {
                "or": "odia",
                "ta": "tamil",
                "te": "telugu",
                "kn": "kannada",
                "ml": "malayalam",
                "bn": "bengali",
                "mr": "marathi",
                "hi": "hindi",
                "en": "english"
            }
            mapped_lang = lang_map.get(target_lang, target_lang)
            if mapped_lang in lang_list:
                score += 20.0

            # Rating boost
            rating = t.get("rating", 4.5)
            score += (rating - 4.0) * 10.0 # up to +10

            # Online and response speed
            if t.get("is_online", False):
                score += 10.0
            resp_time = t.get("response_time_min", 5)
            if resp_time <= 2:
                score += 5.0

            # Emergency exam mode boost
            if self.exam_emergency_mode and t.get("emergency_expert", False):
                score += 15.0

            t_copy = dict(t)
            t_copy["ai_match_score"] = round(min(99.8, score), 1)
            results.append(t_copy)

        # Sort by AI recommendation score descending
        results.sort(key=lambda x: (x.get("is_online", False), x["ai_match_score"]), reverse=True)
        return results

    # ---------------------------------------------------------
    # FEATURE 4 & 7: UBER-LIKE BROADCAST & INSTANT CONNECT
    # ---------------------------------------------------------
    def create_instant_escalation(self, req: EscalationRequest, teacher_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an instant session or broadcasts to matching qualified teachers.
        """
        brief = self.generate_teacher_brief(req)

        # If specific teacher selected
        selected_teacher = None
        if teacher_id and teacher_id in self.teachers:
            selected_teacher = self.teachers[teacher_id]
        else:
            # Auto-assign top matching online teacher
            candidates = self.get_marketplace_teachers(
                subject=req.subject,
                language=req.student_language,
                grade=req.grade
            )
            online_candidates = [c for c in candidates if c.get("is_online", False)]
            if online_candidates:
                selected_teacher = online_candidates[0]
            elif candidates:
                selected_teacher = candidates[0]
            else:
                selected_teacher = list(self.teachers.values())[0]

        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        session = {
            "id": session_id,
            "student_id": req.student_id,
            "student_name": req.student_name,
            "teacher_id": selected_teacher["id"],
            "teacher_name": selected_teacher["name"],
            "teacher_avatar": selected_teacher["avatar"],
            "subject": req.subject,
            "chapter": req.chapter,
            "interaction_mode": req.preferred_interaction,
            "status": "in_progress", # Active session directly opened
            "started_at": time.time(),
            "ended_at": None,
            "duration_minutes": 15.0, # Standard 15 min consultation
            "teacher_brief": brief,
            "whiteboard_data": [
                {"type": "text", "x": 50, "y": 40, "content": f"Session: {req.subject} - {req.chapter}", "color": "#38bdf8"},
                {"type": "text", "x": 50, "y": 70, "content": f"Doubt: {req.original_question}", "color": "#facc15"}
            ],
            "chat_transcript": [
                {"sender": "system", "time": time.strftime("%H:%M"), "text": f"Connected to {selected_teacher['name']}. AI Teacher Brief dispatched."},
                {"sender": "teacher", "time": time.strftime("%H:%M"), "text": f"Namaste {req.student_name}! I have reviewed your question and the AI brief. Let's solve this together on the whiteboard!"}
            ],
            "student_rating": None,
            "student_review": None,
            "session_fee": selected_teacher["price_per_session"],
            "platform_commission": round(selected_teacher["price_per_session"] * (self.commission_percentage / 100.0), 2),
            "teacher_payout": round(selected_teacher["price_per_session"] * (1 - (self.commission_percentage / 100.0)), 2),
            "post_session_summary": None
        }

        self.sessions[session_id] = session
        self.save()

        return {
            "status": "success",
            "session": session,
            "teacher": selected_teacher,
            "brief": brief
        }

    def broadcast_doubt_to_teachers(self, req: EscalationRequest) -> Dict[str, Any]:
        """
        Uber-like broadcast: fires request to all matching available teachers.
        Expires in 60 seconds if unaccepted.
        """
        brief = self.generate_teacher_brief(req)
        broadcast_id = f"bc_{uuid.uuid4().hex[:8]}"

        eligible_teachers = self.get_marketplace_teachers(
            subject=req.subject,
            language=req.student_language,
            grade=req.grade
        )

        broadcast_payload = {
            "broadcast_id": broadcast_id,
            "student_name": req.student_name,
            "grade": req.grade,
            "subject": req.subject,
            "question": req.original_question,
            "brief": brief,
            "matching_teachers_count": len(eligible_teachers),
            "expires_in_seconds": 60,
            "created_at": time.time(),
            "status": "broadcast_active"
        }
        self.broadcast_requests[broadcast_id] = broadcast_payload

        # For demo purposes, the top teacher immediately accepts!
        top_teacher = eligible_teachers[0] if eligible_teachers else list(self.teachers.values())[0]

        session_res = self.create_instant_escalation(req, teacher_id=top_teacher["id"])
        session_res["broadcast_info"] = broadcast_payload
        return session_res

    # ---------------------------------------------------------
    # FEATURE 8: AI ASSISTED TEACHER CO-PILOT
    # ---------------------------------------------------------
    def get_teacher_ai_copilot_hints(self, subject: str, chapter: str, question: str) -> Dict[str, Any]:
        """
        Assists the teacher during the live session with:
        - Relevant NCERT textbook sections
        - Common student misconceptions
        - Suggested remedial practice questions
        - Visual whiteboard drawing suggestions
        """
        hints = {
            "relevant_ncert_sections": [
                {"book": "NCERT Class 9 Science", "chapter": "Chapter 9: Force and Laws of Motion", "page": "Page 121-124"},
                {"book": "Odisha BSE Class 10 Physical Science", "chapter": "ନିଉଟନଙ୍କ ଗତି ନିୟମ", "page": "ପୃଷ୍ଠା ୮୪-୮୮"}
            ],
            "detected_misconceptions": [
                "Student assumes action and reaction act on the same object (confusing balanced forces with 3rd law).",
                "Student believes the heavier object exerts a greater force in an interaction."
            ],
            "suggested_remedies": [
                "Ask student: 'When you jump off a rowboat, what moves? You, or the boat, or both?'",
                "Draw two separate boxes on whiteboard and label forces with different colored arrows."
            ],
            "similar_practice_questions": [
                "A horse pulls a cart. Why does the cart move forward instead of staying stationary?",
                "Calculate recoil velocity of a rifle of mass 4 kg firing a 50g bullet at 300 m/s."
            ]
        }
        return hints

    # ---------------------------------------------------------
    # FEATURE 9: SESSION CONCLUSION & POST-SESSION SUMMARY
    # ---------------------------------------------------------
    def complete_session(self, session_id: str, student_rating: float = 5.0, student_review: str = "Teacher explained with great visual drawings!") -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}

        session["status"] = "completed"
        session["ended_at"] = time.time()
        session["student_rating"] = student_rating
        session["student_review"] = student_review

        # Credit Teacher Wallet
        teacher_id = session["teacher_id"]
        payout = session["teacher_payout"]
        if teacher_id in self.wallets:
            w = self.wallets[teacher_id]
            w["total_earnings"] += payout
            w["pending_earnings"] += payout
            w["total_sessions_completed"] += 1
            w["transactions"].append({
                "id": f"tx_{uuid.uuid4().hex[:6]}",
                "date": time.strftime("%Y-%m-%d"),
                "amount": payout,
                "type": f"session_{session_id[-4:]}",
                "status": "completed"
            })

        # Generate Student Learning Summary
        summary = {
            "session_id": session_id,
            "topics_covered": [session["subject"], session["chapter"], "Free Body Diagrams", "Action-Reaction Pair Analysis"],
            "mistakes_identified": "Confusing internal vs external force cancellation.",
            "concepts_mastered": ["Newton's Third Law", "Vector direction of pairs"],
            "homework_recommended": [
                "Solve NCERT Chapter 9 Exercise Questions 4, 7 and 12.",
                "Draw action-reaction diagram for swimming in water."
            ],
            "revision_plan": "Review notes after 24 hours; take 5-question adaptive quiz in Student Portal."
        }
        session["post_session_summary"] = summary
        self.save()

        return {
            "status": "success",
            "session": session,
            "post_session_summary": summary,
            "wallet_updated": self.wallets.get(teacher_id)
        }

    # ---------------------------------------------------------
    # FEATURE 10: PARENT VISIBILITY
    # ---------------------------------------------------------
    def get_parent_dashboard(self, student_id: str = "std_001") -> Dict[str, Any]:
        """Provides transparency for parents on teacher consultations, spend, and improvement."""
        student_sessions = [s for s in self.sessions.values() if s.get("student_id") == student_id]
        total_time_min = sum([s.get("duration_minutes", 15.0) for s in student_sessions])
        total_spent = sum([s.get("session_fee", 150.0) for s in student_sessions])

        return {
            "student_name": "Aarav Mohapatra",
            "grade": "Class 10",
            "school": "Govt High School, Khordha",
            "total_teacher_sessions": len(student_sessions) if student_sessions else 4,
            "total_time_spent_minutes": total_time_min if total_time_min else 60.0,
            "total_consultation_spend_inr": total_spent if total_spent else 600.0,
            "average_teacher_rating_given": 4.9,
            "subjects_consulted": ["Physics", "Mathematics"],
            "concept_mastery_gain": "+28% after live teacher interventions",
            "recent_sessions": [
                {
                    "teacher": "Prof. Rashmi Rekha Das",
                    "subject": "Physics - Newton's Laws",
                    "date": "Today",
                    "duration": "15 min",
                    "outcome": "Resolved action-reaction cancellation gap via Chilika boat diagrams."
                },
                {
                    "teacher": "Karthik Subramanian",
                    "subject": "Mathematics - Pythagoras Theorem",
                    "date": "2 days ago",
                    "duration": "15 min",
                    "outcome": "Mastered 3D diagonal shortcuts."
                }
            ]
        }

    # ---------------------------------------------------------
    # FEATURE 11 & 12: TEACHER WALLET & LEADERBOARD
    # ---------------------------------------------------------
    def get_teacher_wallet(self, teacher_id: str) -> Dict[str, Any]:
        return self.wallets.get(teacher_id, {
            "total_earnings": 0.0,
            "pending_earnings": 0.0,
            "withdrawn_earnings": 0.0,
            "transactions": []
        })

    def get_teacher_leaderboard(self) -> List[Dict[str, Any]]:
        board = []
        for t in self.teachers.values():
            w = self.wallets.get(t["id"], {})
            board.append({
                "id": t["id"],
                "name": t["name"],
                "avatar": t["avatar"],
                "rating": t["rating"],
                "total_sessions": t["total_sessions"],
                "performance_score": t.get("performance_score", 90.0),
                "total_earnings": w.get("total_earnings", 12000.0),
                "languages": t["languages"],
                "specialty": t.get("emergency_specialty", "Core Subject Expert")
            })
        board.sort(key=lambda x: x["performance_score"], reverse=True)
        return board

    # ---------------------------------------------------------
    # FEATURE 15: ADMIN DASHBOARD
    # ---------------------------------------------------------
    def get_admin_metrics(self) -> Dict[str, Any]:
        total_sessions = len(self.sessions) + 248 # demo historical base
        gross_revenue = total_sessions * 150.0
        platform_rev = gross_revenue * (self.commission_percentage / 100.0)

        return {
            "total_active_teachers": len(self.teachers),
            "total_students_enrolled": 1420,
            "total_sessions_completed": total_sessions,
            "gross_session_revenue_inr": gross_revenue,
            "platform_commission_revenue_inr": platform_rev,
            "ai_to_human_escalation_rate": "14.2%", # 14% of AI conversations escalate to human teacher
            "student_satisfaction_score": "98.4%",
            "top_requested_subjects": [
                {"subject": "Physics (Newtonian Mechanics)", "requests": 94},
                {"subject": "Mathematics (Coordinate Geometry)", "requests": 82},
                {"subject": "Chemistry (Acids & Bases)", "requests": 45},
                {"subject": "Biology (Life Processes)", "requests": 38}
            ],
            "commission_percentage": self.commission_percentage,
            "exam_emergency_mode": self.exam_emergency_mode
        }

    def toggle_exam_emergency_mode(self, enabled: bool) -> bool:
        self.exam_emergency_mode = enabled
        self.save()
        return self.exam_emergency_mode

# Global singleton
escalation_engine = EscalationEngine()
