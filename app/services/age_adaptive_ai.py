"""
AGE-ADAPTIVE AI PROFILING SERVICE
Adapts AI questions, language, and recommendations based on user age
"""

from typing import Dict, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
import json

from app.core.config import settings

# Age group definitions
class AgeGroup:
    KIDS = "kids"  # 5-12
    TEENS = "teens"  # 13-17
    YOUNG_ADULT = "young_adult"  # 18-24
    ADULT = "adult"  # 25-44
    MIDDLE_AGE = "middle_age"  # 45-60
    SENIOR = "senior"  # 60+


def get_age_group(age: int) -> str:
    """Determine age group from age"""
    if 5 <= age <= 12:
        return AgeGroup.KIDS
    elif 13 <= age <= 17:
        return AgeGroup.TEENS
    elif 18 <= age <= 24:
        return AgeGroup.YOUNG_ADULT
    elif 25 <= age <= 44:
        return AgeGroup.ADULT
    elif 45 <= age <= 60:
        return AgeGroup.MIDDLE_AGE
    else:
        return AgeGroup.SENIOR


class AgeAdaptiveAIService:
    """AI service that adapts to user's age group"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def get_ai_personality(self, age_group: str) -> Dict:
        """Get AI personality configuration for age group"""

        personalities = {
            AgeGroup.KIDS: {
                "tone": "enthusiastic, encouraging, simple, playful",
                "language_level": "elementary (ages 5-12)",
                "emoji_frequency": "high (every sentence)",
                "sentence_length": "short (5-10 words)",
                "vocabulary": "simple words only, no jargon",
                "examples": [
                    "Wow! You love art! That's so cool! 🎨✨",
                    "Great choice! Let's find fun drawing classes for you! 🌟",
                ],
            },
            AgeGroup.TEENS: {
                "tone": "casual, relatable, hype, trendy",
                "language_level": "high school (ages 13-17)",
                "emoji_frequency": "medium-high",
                "sentence_length": "medium (10-15 words)",
                "vocabulary": "appropriate slang, no cringe",
                "references": "current trends (respectfully)",
                "examples": [
                    "Yo! Content creation? That's 🔥! Let's get you started.",
                    "Bet! I found some sick courses for you to check out 👀",
                ],
            },
            AgeGroup.YOUNG_ADULT: {
                "tone": "professional yet friendly, direct",
                "language_level": "college/professional",
                "emoji_frequency": "low (sparingly)",
                "sentence_length": "medium-long (15-20 words)",
                "vocabulary": "professional, industry terms okay",
                "focus": "outcomes, ROI, career impact",
                "examples": [
                    "Got it! UI Design with a focus on career transition. Let's build you a roadmap.",
                ],
            },
            AgeGroup.ADULT: {
                "tone": "professional, consultative, efficient",
                "language_level": "professional/executive",
                "emoji_frequency": "minimal",
                "sentence_length": "medium-long",
                "vocabulary": "professional, business terminology",
                "focus": "ROI, efficiency, credentials, results",
                "examples": [
                    "Understood. Let's create a pathway to your promotion goal.",
                ],
            },
            AgeGroup.MIDDLE_AGE: {
                "tone": "respectful, empowering, thoughtful",
                "language_level": "professional, mature",
                "emoji_frequency": "none to minimal",
                "sentence_length": "medium",
                "vocabulary": "professional, mature",
                "focus": "purpose, legacy, impact, fulfillment",
                "examples": [
                    "Your 25 years of experience would be incredibly valuable to aspiring professionals.",
                ],
            },
            AgeGroup.SENIOR: {
                "tone": "patient, warm, respectful, supportive",
                "language_level": "clear, simple (not condescending)",
                "emoji_frequency": "minimal",
                "sentence_length": "short-medium",
                "vocabulary": "clear, familiar terms",
                "pace": "slow, deliberate",
                "focus": "community, enjoyment, support, ease of use",
                "examples": [
                    "That's wonderful! Art classes can be very rewarding. Let me find some beginner-friendly options for you.",
                ],
            },
        }

        return personalities.get(age_group, personalities[AgeGroup.YOUNG_ADULT])

    def get_questions_for_age_group(self, age_group: str) -> List[Dict]:
        """Get age-appropriate profiling questions"""

        questions = {
            AgeGroup.KIDS: [
                {
                    "step": 1,
                    "question": "Hi! I'm Sooshi, your learning buddy! 🌟 What's your name?",
                    "input_type": "text",
                    "voice_enabled": True,
                },
                {
                    "step": 2,
                    "question": "What do you LOVE to do for fun? 🎨🎮⚽🎵",
                    "options": [
                        {"emoji": "🎨", "label": "Drawing & Art", "value": "art"},
                        {"emoji": "🎮", "label": "Video Games", "value": "gaming"},
                        {"emoji": "⚽", "label": "Sports", "value": "sports"},
                        {"emoji": "🎵", "label": "Music & Dance", "value": "music"},
                        {"emoji": "📚", "label": "Reading Stories", "value": "reading"},
                        {"emoji": "🧪", "label": "Science", "value": "science"},
                    ],
                    "input_type": "multi_select_visual",
                    "max_selections": 3,
                },
                {
                    "step": 3,
                    "question": "How much time do you want to spend learning? ⏰",
                    "options": [
                        {"label": "Just a little (15 mins)", "value": "15min"},
                        {"label": "Some time (30 mins)", "value": "30min"},
                        {"label": "Lots of time (1 hour)", "value": "60min"},
                    ],
                    "input_type": "single_select",
                },
            ],
            AgeGroup.TEENS: [
                {
                    "step": 1,
                    "question": "Hey! Welcome to Soosh 👋 What should we call you?",
                    "input_type": "text",
                },
                {
                    "step": 2,
                    "question": "What gets you hyped? Pick up to 3! 🔥",
                    "options": [
                        {"emoji": "🎨", "label": "Design & Art", "trending": True},
                        {"emoji": "💻", "label": "Coding & Tech", "trending": True},
                        {"emoji": "📱", "label": "Social Media", "trending": True},
                        {"emoji": "💰", "label": "Side Hustles", "trending": True},
                    ],
                    "input_type": "multi_select_cards",
                    "max_selections": 3,
                },
                {
                    "step": 3,
                    "question": "Why are you here? (Be real!)",
                    "options": [
                        "Make money / side hustle 💸",
                        "Get a job or internship 💼",
                        "College prep 🎓",
                        "Build my personal brand 📱",
                    ],
                    "input_type": "multi_select",
                },
            ],
            AgeGroup.YOUNG_ADULT: [
                {
                    "step": 1,
                    "question": "What brings you here today?",
                    "options": [
                        "Career transition",
                        "Level up current skills",
                        "Start a side hustle",
                        "Find a mentor",
                    ],
                    "input_type": "multi_select",
                },
                {
                    "step": 2,
                    "question": "What skills are you interested in?",
                    "input_type": "search_multi_select",
                    "placeholder": "Type to search... (e.g., UI Design, Python)",
                },
                {
                    "step": 3,
                    "question": "What's your timeline?",
                    "options": [
                        {"label": "ASAP (1-3 months)", "value": "urgent"},
                        {"label": "This year (3-6 months)", "value": "medium"},
                        {"label": "Flexible (6-12 months)", "value": "relaxed"},
                    ],
                    "input_type": "single_select_cards",
                },
            ],
            # ... other age groups
        }

        return questions.get(age_group, questions[AgeGroup.YOUNG_ADULT])

    async def generate_age_appropriate_response(
        self, age_group: str, user_message: str, conversation_history: List[Dict]
    ) -> str:
        """Generate AI response adapted to age group"""

        personality = self.get_ai_personality(age_group)

        system_prompt = f"""
You are Sooshi, the AI assistant for Soosh learning platform.

USER AGE GROUP: {age_group}

PERSONALITY GUIDELINES:
- Tone: {personality['tone']}
- Language level: {personality['language_level']}
- Emoji frequency: {personality['emoji_frequency']}
- Sentence length: {personality.get('sentence_length', 'medium')}
- Vocabulary: {personality['vocabulary']}

{f"Focus: {personality['focus']}" if 'focus' in personality else ''}

EXAMPLES OF YOUR STYLE:
{chr(10).join([f"- {ex}" for ex in personality['examples']])}

IMPORTANT RULES:
1. Be age-appropriate and respectful
2. For kids: Use simple words, be encouraging, add fun emojis
3. For teens: Be relatable, use appropriate slang, be hype
4. For young adults: Be professional but friendly, focus on outcomes
5. For adults: Be efficient, consultative, ROI-focused
6. For middle age: Be respectful, emphasize purpose and impact
7. For seniors: Be patient, clear, supportive

Respond to the user's message in this style.
"""

        messages = [{"role": "system", "content": system_prompt}] + conversation_history + [
            {"role": "user", "content": user_message}
        ]

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL, messages=messages, temperature=0.7, max_tokens=200
        )

        return response.choices[0].message.content

    async def extract_profile_data(
        self, age_group: str, conversation_history: List[Dict]
    ) -> Dict:
        """Extract structured profile data from conversation"""

        extraction_prompt = f"""
Analyze this onboarding conversation with a {age_group} user and extract:

1. Interests/Passions (as array of strings)
2. Skills (as array of {{skill: string, level: string}})
3. Goals (as single string)
4. Time commitment (as string)
5. Learning style (as string: visual, hands-on, theoretical, mentorship)
6. Motivation (why they're here)

For kids/teens: Simplify and focus on fun interests
For adults: Focus on career and ROI
For seniors: Focus on enjoyment and community

Return ONLY a JSON object, no other text.

Example output:
{{
  "passions": ["Art", "Design"],
  "skills": [{{"skill": "Drawing", "level": "beginner"}}],
  "goals": "Learn digital art",
  "time_commitment": "30 minutes/day",
  "learning_style": "visual",
  "motivation": "creative expression"
}}
"""

        messages = conversation_history + [
            {"role": "system", "content": extraction_prompt}
        ]

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        profile_data = json.loads(response.choices[0].message.content)

        return profile_data

    def filter_opportunities_by_age(
        self, opportunities: List[Dict], age_group: str
    ) -> List[Dict]:
        """Filter opportunities appropriate for age group"""

        age_filters = {
            AgeGroup.KIDS: {
                "difficulty": ["beginner"],
                "content_rating": ["all_ages", "kids"],
                "max_duration": 30,  # minutes
            },
            AgeGroup.TEENS: {
                "difficulty": ["beginner", "intermediate"],
                "content_rating": ["all_ages", "teen"],
                "max_duration": 60,
            },
            AgeGroup.YOUNG_ADULT: {
                "difficulty": ["all"],
                "content_rating": ["all"],
            },
            # ... other groups
        }

        filters = age_filters.get(age_group, {"difficulty": ["all"]})

        # Apply filters to opportunities
        filtered = []
        for opp in opportunities:
            if filters.get("difficulty") and opp.get("difficulty") not in filters[
                "difficulty"
            ]:
                continue
            if filters.get("max_duration") and opp.get("duration_minutes", 0) > filters[
                "max_duration"
            ]:
                continue

            filtered.append(opp)

        return filtered

    def get_parental_consent_requirements(self, age_group: str) -> Dict:
        """Get parental consent requirements for age group"""

        if age_group == AgeGroup.KIDS:
            return {
                "required": True,
                "level": "full",
                "features_restricted": [
                    "payments",
                    "direct_messaging",
                    "external_links",
                    "profile_public",
                ],
                "message": "For safety, we need a parent or guardian to set up and manage your account.",
            }
        elif age_group == AgeGroup.TEENS:
            return {
                "required": True,
                "level": "partial",
                "features_restricted": ["payments_over_50", "mentor_sessions_unsupervised"],
                "message": "We may need parental consent for some features.",
            }
        else:
            return {"required": False, "level": "none", "features_restricted": []}
