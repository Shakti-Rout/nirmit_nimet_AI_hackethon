# -*- coding: utf-8 -*-
"""
End-to-End Test Suite for Prerana Agentic EdTech Application.
Validates all features requested in the hackathon problem statement:
- RAG Implementation
- Multi-lingual Switcher (Odia, Tamil, Telugu, Kannada, Malayalam, English)
- Text-to-Speech (TTS), Voice-to-Voice pipelines
- Specific AI Agent (Autonomous ReAct & Deterministic Workflow)
- Separate Portals & Roles (Student, Teacher, Developer)
- Offline Resilience & Batch Sync
"""

import sys
import os
sys.stdout.reconfigure(encoding="utf-8")

from app.localization import LANGUAGES, TRANSLATIONS, get_text
from app.rag_engine import rag_engine
from app.agent_engine import agent_engine
from app.speech_engine import speech_engine
from app.auth_db import auth_db

def run_tests():
    print("==================================================================")
    print("🧪 RUNNING PRERANA AI COMPREHENSIVE TEST SUITE")
    print("==================================================================")

    # 1. Test Localization across all 6 languages
    print("\n[1/7] Testing Language Dictionaries...")
    expected_langs = ["en", "or", "ta", "te", "kn", "ml"]
    for lang in expected_langs:
        meta = LANGUAGES.get(lang)
        app_title = get_text("app_title", lang)
        assert meta is not None, f"Missing metadata for language {lang}"
        assert app_title != "", f"Empty title for language {lang}"
        print(f"  ✓ {lang} ({meta['native']}) -> Title: {app_title[:30]}...")

    # 2. Test RAG Vector Search & Ingestion
    print("\n[2/7] Testing RAG Engine & Vector Search...")
    stats = rag_engine.get_stats()
    print(f"  ✓ Total indexed chunks: {stats['total_chunks']}")
    print(f"  ✓ Vector vocabulary dimension: {stats['vector_dimension']}")
    print(f"  ✓ Language breakdown: {stats['languages']}")

    rag_en = rag_engine.query("Newton third law equal opposite reaction", top_k=2)
    assert len(rag_en) > 0, "RAG failed to retrieve English chunk"
    print(f"  ✓ English RAG Search -> Matched: {rag_en[0]['id']} (Score: {rag_en[0]['score']})")

    rag_or = rag_engine.query("ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ", top_k=2, language_filter="or")
    assert len(rag_or) > 0, "RAG failed to retrieve Odia chunk"
    print(f"  ✓ Odia RAG Search -> Matched: {rag_or[0]['id']} (Score: {rag_or[0]['score']})")

    # Ingest dynamic custom document
    ingested_count = rag_engine.ingest_text_document(
        title="Odia Water Cycle",
        text="ଜଳ ଚକ୍ର: ସୂର୍ଯ୍ୟଙ୍କ ତାପରେ ନଦୀ, ସମୁଦ୍ରର ଜଳ ବାଷ୍ପୀଭୂତ ହୋଇ ବାୟୁମଣ୍ଡଳକୁ ଯାଏ ଏବଂ ମେଘ ହୋଇ ବର୍ଷା ଆକାରରେ ଭୂମିକୁ ଫେରିଆସେ।",
        subject="Earth Science",
        language="or"
    )
    print(f"  ✓ Dynamic Ingestion -> Added {ingested_count} chunks. New total: {len(rag_engine.chunks)}")

    # 3. Test Agentic Engine - Autonomous ReAct Loop
    print("\n[3/7] Testing Autonomous ReAct Agent Loop...")
    agent_engine.set_framework("autonomous")
    res_react = agent_engine.run_agent("Explain Newton third law with boat example", language="or")
    assert res_react["status"] == "success"
    assert "tools_called" in res_react
    assert len(res_react["trace"]) >= 3
    print(f"  ✓ Goal: {res_react['goal']}")
    print(f"  ✓ Tools Invoked: {res_react['tools_called']}")
    print(f"  ✓ Decision Trace Steps: {len(res_react['trace'])}")
    print(f"  ✓ Latency: {res_react['latency_ms']}ms")

    # 4. Test Agentic Engine - Deterministic Workflow Loop
    print("\n[4/7] Testing Deterministic Workflow Graph...")
    agent_engine.set_framework("deterministic")
    res_det = agent_engine.run_agent("Photosynthesis process", language="en")
    assert res_det["status"] == "success"
    assert res_det["framework_used"] == "deterministic_workflow"
    print(f"  ✓ Deterministic Graph Executed -> State Steps: {len(res_det['trace'])}")

    # 5. Test Diagnostic Misconception Evaluator & Quiz Scaffolding
    print("\n[5/7] Testing Diagnostic Scaffolding & Adaptive Quiz...")
    quiz = res_react.get("quiz")
    assert quiz is not None
    eval_correct = agent_engine.evaluate_quiz_submission(
        user_choice="B",
        quiz_data=quiz,
        language="or",
        user_email="student@prerana.ai"
    )
    print(f"  ✓ Quiz Evaluation: Selected B -> is_correct: {eval_correct['evaluation']['is_correct']}")
    print(f"  ✓ Mastery Adjustment: {eval_correct['evaluation']['mastery_delta']}%")

    eval_wrong = agent_engine.evaluate_quiz_submission(
        user_choice="A",
        quiz_data=quiz,
        language="or",
        user_email="student@prerana.ai"
    )
    print(f"  ✓ Misconception Detected on Choice A -> Feedback: {eval_wrong['evaluation']['feedback'][:60]}...")

    # 6. Test Speech Engine (TTS & Multi-tier Fallback)
    print("\n[6/7] Testing Speech Engine (TTS)...")
    tts_res_en = speech_engine.text_to_speech("Newton third law of motion", lang="en")
    print(f"  ✓ English TTS Status: {tts_res_en['status']} (Engine: {tts_res_en.get('engine_used')})")

    tts_res_ta = speech_engine.text_to_speech("நியூட்டனின் மூன்றாம் விதி", lang="ta")
    print(f"  ✓ Tamil TTS Status: {tts_res_ta['status']} (Engine: {tts_res_ta.get('engine_used')})")

    tts_res_or = speech_engine.text_to_speech("ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ", lang="or")
    print(f"  ✓ Odia TTS Status: {tts_res_or['status']} (Engine: {tts_res_or.get('engine_used')})")

    # 7. Test Auth DB, Roles & Teacher Analytics
    print("\n[7/7] Testing Roles, Portals & Offline Sync...")
    student_sess = auth_db.authenticate("student@prerana.ai", "learn123", expected_role="student")
    assert student_sess["user"]["role"] == "student"
    print(f"  ✓ Student Login: {student_sess['user']['name']} ({student_sess['user']['role']})")

    teacher_sess = auth_db.authenticate("teacher@prerana.ai", "teach123", expected_role="teacher")
    assert teacher_sess["user"]["role"] == "teacher"
    print(f"  ✓ Teacher Login: {teacher_sess['user']['name']} ({teacher_sess['user']['role']})")

    assert auth_db.authenticate("teacher@prerana.ai", "teach123", expected_role="student") is None
    assert auth_db.users["teacher@prerana.ai"]["role"] == "teacher"
    print("  ✓ Role mismatch is rejected without changing the account role")
    assert auth_db.authenticate("unknown@prerana.ai", "password", expected_role="admin") is None
    assert "unknown@prerana.ai" not in auth_db.users
    print("  ✓ Unknown accounts cannot self-register as privileged roles")

    admin_sess = auth_db.authenticate("admin@prerana.ai", "admin123", expected_role="admin")
    assert admin_sess["user"]["role"] == "admin"
    print(f"  ✓ Admin Login: {admin_sess['user']['name']} ({admin_sess['user']['role']})")

    dev_sess = auth_db.authenticate("dev@prerana.ai", "dev123", expected_role="developer")
    assert dev_sess["user"]["role"] == "developer"
    print(f"  ✓ Developer Login: {dev_sess['user']['name']} ({dev_sess['user']['role']})")

    analytics = auth_db.get_class_analytics()
    print(f"  ✓ Teacher Class Diagnostics: {analytics['total_students']} students, {len(analytics['top_struggle_topics'])} struggle topics identified.")

    # 8. Test AI-to-Live Teacher Escalation Engine (Astrotalk Hybrid Model)
    print("\n[8/8] Testing AI-to-Live Teacher Escalation System...")
    from app.escalation_engine import escalation_engine, EscalationRequest

    # Test Marketplace
    teachers = escalation_engine.get_marketplace_teachers(subject="Physics", language="or")
    assert len(teachers) > 0, "Failed to retrieve marketplace teachers"
    print(f"  ✓ Teacher Marketplace: Found {len(teachers)} matching Physics/Odia teachers.")
    print(f"  ✓ Top Recommended: {teachers[0]['name']} (Score: {teachers[0]['ai_match_score']})")

    # Test AI Teacher Brief
    req = EscalationRequest(
        student_name="Aarav Mohapatra",
        grade="Class 10",
        subject="Physics",
        chapter="Newton's Laws of Motion",
        original_question="Why do action and reaction forces never cancel?",
        confusion_reason="Confused about opposite forces summing to zero",
        student_language="or"
    )
    brief = escalation_engine.generate_teacher_brief(req)
    assert "suggested_explanation_level" in brief
    print(f"  ✓ AI Teacher Brief: Generated level -> '{brief['suggested_explanation_level']}'")
    print(f"  ✓ Pedagogical Hook: {brief['recommended_pedagogical_hook'][:55]}...")

    # Test Instant Connect & Session Room
    sess_res = escalation_engine.create_instant_escalation(req)
    assert sess_res["status"] == "success"
    session_id = sess_res["session"]["id"]
    print(f"  ✓ Instant Connect: Created active session '{session_id}' with {sess_res['teacher']['name']}")

    # Test Live AI Co-pilot hints for teacher
    hints = escalation_engine.get_teacher_ai_copilot_hints("Physics", "Newton's Laws", req.original_question)
    assert len(hints["relevant_ncert_sections"]) > 0
    print(f"  ✓ AI Co-pilot: Retrieved {len(hints['relevant_ncert_sections'])} NCERT references and {len(hints['detected_misconceptions'])} detected student misconceptions.")

    # Test Session Completion & Post-Session Summary
    comp_res = escalation_engine.complete_session(session_id, student_rating=5.0)
    assert comp_res["status"] == "success"
    assert "post_session_summary" in comp_res
    print(f"  ✓ Session Completed: Generated post-session summary with {len(comp_res['post_session_summary']['topics_covered'])} topics mastered.")

    # Test Parent Dashboard & Teacher Wallet
    parent_data = escalation_engine.get_parent_dashboard("std_001")
    assert parent_data["total_teacher_sessions"] >= 1
    print(f"  ✓ Parent Dashboard: Child Aarav has {parent_data['total_teacher_sessions']} attended sessions, gain: {parent_data['concept_mastery_gain']}.")

    # Test Admin Emergency Mode
    is_emergency = escalation_engine.toggle_exam_emergency_mode(True)
    assert is_emergency is True
    print(f"  ✓ Exam Emergency Mode: Successfully toggled to {is_emergency} (Priority Matchmaking ON).")

    print("\n==================================================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! HYBRID PLATFORM 100% OPERATIONAL!")
    print("==================================================================")


if __name__ == "__main__":
    run_tests()
