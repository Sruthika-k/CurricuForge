from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from transformers import pipeline

logger = logging.getLogger(__name__)


_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"

load_dotenv(_ENV_PATH)

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
_HF_API_KEY = os.getenv("HF_API_KEY")
_HF_CLASSIFIER_MODEL = os.getenv(
    "HF_CLASSIFIER_MODEL", "distilbert-base-uncased-finetuned-sst-2-english"
)

_gemini_client = genai.Client(api_key=_GEMINI_API_KEY) if _GEMINI_API_KEY else None


_text_classifier = pipeline(
    "text-classification",
    model=_HF_CLASSIFIER_MODEL,
    token=_HF_API_KEY,
) if _HF_API_KEY else None


async def generate_curriculum(
    subject: str,
    level: str,
    duration: str,
    goals: str,
) -> str:
    subject_text = subject.strip() or "Untitled course"
    level_text = level.strip() or "Not specified"
    duration_text = duration.strip() or "Not specified"
    goals_text = goals.strip() or "(No goals provided)"

    # HuggingFace classification
    print("HF started")
    logger.info("HuggingFace classification started")
    classification_summary = _classify_goals(goals_text)
    logger.info("HuggingFace classification completed")
    print("HF finished")

    if _gemini_client is None:
        return _fallback_curriculum(
            subject_text,
            level_text,
            duration_text,
            goals_text,
            classification_summary,
        )

    prompt = _build_prompt(
        subject=subject_text,
        level=level_text,
        duration=duration_text,
        goals=goals_text,
    )

    # Gemini API call
    print("Gemini call started")
    logger.info("Gemini call started")
    try:
        response = _gemini_client.models.generate_content(
            model=_GEMINI_MODEL_NAME,
            contents=prompt
        )
        generated_text = (response.text or "").strip()
        logger.info("Gemini call completed")
        print("Gemini call finished")
    except Exception as e:
        error_message = f"Gemini API Error: {str(e)}"
        logger.error(f"Gemini call failed: {e}")
        print("Gemini call finished")
        return error_message

    if not generated_text:
        return _fallback_curriculum(
            subject_text,
            level_text,
            duration_text,
            goals_text,
            classification_summary,
        )

    # Add skill analysis if available, but return curriculum even if classification failed
    skill_analysis = f"AI Skill Analysis\n{classification_summary}" if classification_summary else "AI Skill Analysis\nClassification unavailable."

    return "\n\n".join([generated_text.strip(), skill_analysis]).strip()


def classify_course(subject: str, goals: str) -> dict:
    subject_lower = subject.lower()
    goals_lower = goals.lower()
    combined = f"{subject_lower} {goals_lower}"
    
    technical_keywords = [
        "programming", "coding", "software", "data", "machine learning", "ai",
        "python", "java", "javascript", "web", "app", "database", "sql",
        "algorithm", "computer", "development", "engineering", "cloud",
        "devops", "api", "framework", "library", "neural", "deep learning",
        "analytics", "visualization", "statistics", "r programming"
    ]
    
    creative_keywords = [
        "design", "art", "creative", "writing", "music", "media",
        "photography", "video", "graphic", "ux", "ui"
    ]
    
    conceptual_keywords = [
        "theory", "philosophy", "ethics", "history", "literature",
        "social", "psychology", "economics", "policy", "research"
    ]
    
    certification_keywords = [
        "certification", "exam", "prep", "test", "certificate"
    ]
    
    action_verbs = {
        "build": ["build", "construct", "develop", "create"],
        "analyze": ["analyze", "examine", "investigate", "evaluate"],
        "implement": ["implement", "apply", "execute", "deploy"],
        "design": ["design", "architect", "plan", "model"],
        "understand": ["understand", "comprehend", "learn", "grasp"]
    }
    
    is_technical = any(keyword in combined for keyword in technical_keywords)
    is_creative = any(keyword in combined for keyword in creative_keywords)
    is_conceptual = any(keyword in combined for keyword in conceptual_keywords)
    is_certification = any(keyword in combined for keyword in certification_keywords)
    
    detected_verbs = []
    for verb_category, verb_list in action_verbs.items():
        if any(verb in goals_lower for verb in verb_list):
            detected_verbs.append(verb_category)
    
    if is_technical:
        emphasis = "hands-on"
    elif is_creative:
        emphasis = "hands-on"
    elif is_conceptual or is_certification:
        emphasis = "conceptual"
    else:
        emphasis = "hands-on" if detected_verbs else "conceptual"
    
    return {
        "is_technical": is_technical,
        "emphasis": emphasis,
        "detected_verbs": detected_verbs
    }


def build_dynamic_prompt(
    subject: str,
    level: str,
    duration: str,
    goals: str
) -> str:
    duration_weeks = duration.replace(" weeks", "").strip()
    course_profile = classify_course(subject, goals)
    
    base_prompt = f"""You are an expert academic curriculum designer and educator.

Create a highly detailed, practical, and subject-specific curriculum.

Subject: {subject}
Level: {level}
Duration: {duration_weeks} weeks
Stated Goals:
{goals}

"""
    
    adaptive_instructions = []
    
    if course_profile["is_technical"]:
        adaptive_instructions.append("""TECHNICAL COURSE REQUIREMENTS:
- Specify real tools, libraries, frameworks, and technologies by name
- Include hands-on coding assignments with clear deliverables
- Design a capstone project that integrates multiple concepts
- Include deployment or real-world implementation steps
- Provide setup instructions for development environments
- Reference official documentation and resources""")
    
    if course_profile["emphasis"] == "conceptual":
        adaptive_instructions.append("""CONCEPTUAL COURSE REQUIREMENTS:
- Include case study discussions with real-world examples
- Design reflection activities that deepen understanding
- Provide theoretical grounding with academic references
- Include critical analysis exercises
- Encourage synthesis of ideas across topics""")
    
    if "build" in course_profile["detected_verbs"] or "implement" in course_profile["detected_verbs"]:
        adaptive_instructions.append("""PROJECT-BASED LEARNING EMPHASIS:
- Structure curriculum around building tangible outputs
- Each week should contribute to a larger project
- Include iterative development cycles
- Provide clear milestones and deliverables
- Emphasize practical application over theory""")
    
    if "analyze" in course_profile["detected_verbs"]:
        adaptive_instructions.append("""ANALYTICAL THINKING EMPHASIS:
- Include data analysis and interpretation tasks
- Design exercises that require critical evaluation
- Provide frameworks for systematic analysis
- Include comparative studies and assessments""")
    
    if level.lower() == "beginner":
        adaptive_instructions.append("""BEGINNER LEVEL ADAPTATIONS:
- Include foundational explanations and prerequisites
- Provide scaffolding with step-by-step guidance
- Start with simplified examples before complexity
- Include glossary of key terms
- Offer additional support resources
- Design low-stakes practice opportunities""")
    elif level.lower() == "intermediate":
        adaptive_instructions.append("""INTERMEDIATE LEVEL ADAPTATIONS:
- Assume foundational knowledge exists
- Include applied projects with real-world context
- Introduce industry best practices
- Challenge students with problem-solving scenarios
- Include peer collaboration opportunities""")
    elif level.lower() == "advanced":
        adaptive_instructions.append("""ADVANCED LEVEL ADAPTATIONS:
- Include industry-level complexity and scale
- Incorporate research elements and cutting-edge topics
- Design open-ended challenges with multiple solutions
- Reference academic papers and advanced resources
- Include optimization and performance considerations
- Expect independent problem-solving""")
    
    adaptive_section = "\n\n".join(adaptive_instructions)
    
    requirements = f"""
{adaptive_section}

CORE REQUIREMENTS:

1. Make the curriculum SPECIFIC to {subject} - no generic templates
2. Break down each week with:
   - Specific topics and subtopics
   - Practical activities with clear instructions
   - Tools/resources needed
   - Assignment description with deliverables
3. Align all assignments directly with the stated goals
4. Ensure logical progression from foundations to application
5. Use concrete examples, not abstract placeholders
6. Provide enough detail for a new instructor to teach directly from this

Structure output in these sections:

Course Overview
Weekly Breakdown (Week 1 to Week {duration_weeks})
Assignments (Detailed)
Learning Outcomes (Measurable & skill-based)
Alignment to Stated Goals (Explicit mapping)

Make this curriculum immediately usable and subject-specific."""
    
    return base_prompt + requirements


def _build_prompt(
    subject: str,
    level: str,
    duration: str,
    goals: str,
) -> str:
    return build_dynamic_prompt(subject, level, duration, goals)


def _classify_goals(goals: str) -> str:
    if not goals or goals.strip() == "(No goals provided)":
        return "No explicit goals provided."

    if _text_classifier is None:
        return "Classification model not configured."

    try:
        result = _text_classifier(goals, truncation=True, max_length=256)
    except Exception:
        return "Classification unavailable."

    if isinstance(result, list) and result:
        top = result[0]
        label = str(top.get("label", "UNKNOWN"))
        score = float(top.get("score", 0.0))
        return f"Primary intent: {label} (confidence {score:.2f})."

    return "Classification unavailable."


def _fallback_curriculum(
    subject: str,
    level: str,
    duration: str,
    goals: str,
    classification_summary: str,
) -> str:
    lines = [
        "CurricuForge Curriculum Draft (offline mode)",
        f"Subject: {subject}",
        f"Level: {level}",
        f"Duration: {duration}",
        "",
        f"Goals classification: {classification_summary}",
        "",
        "Course Overview:",
        "- This is a structured starting point you can refine.",
        "- Once Gemini is configured, richer drafts will be generated automatically.",
        "",
        "Weekly Breakdown (example skeleton):",
        "Week 1 – Orientation and foundations",
        "  • Introduce core concepts and expectations.",
        "  • Establish baseline understanding through a short diagnostic activity.",
        "Week 2 – Building core skills",
        "  • Targeted practice on foundational skills.",
        "  • Low-stakes formative assessment to surface misconceptions.",
        "Week 3 – Application in context",
        "  • Apply skills to realistic or local examples.",
        "  • Short reflective assignment connecting learning to learners' contexts.",
        "Week 4+ – Deepening, projects, and assessment",
        "  • Alternate between new material and consolidation.",
        "  • Sequence checkpoints and a culminating task aligned with your outcomes.",
        "",
        "Assignments (outline):",
        "- Diagnostic task to surface prior knowledge.",
        "- Practice set focused on core skills.",
        "- Contextual project connecting learning to learners' environment.",
        "- Culminating assessment aligned to the stated goals.",
        "",
        "Learning Outcomes (examples):",
        "- Learners can describe the core concepts of the subject.",
        "- Learners can apply foundational skills to simple, authentic tasks.",
        "- Learners can reflect on their own progress and identify next steps.",
    ]

    if goals and goals != "(No goals provided)":
        lines.extend([
            "",
            "Stated goals / outcomes (verbatim):",
            goals,
        ])

    return "\n".join(lines).strip()
