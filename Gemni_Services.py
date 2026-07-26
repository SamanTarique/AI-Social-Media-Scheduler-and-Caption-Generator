import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from Rag import search_knowledge

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

API_KEY = os.getenv("Saman2_api")
client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
You are an AI Social Media Marketing Assistant for Foodpanda.

Your task is to generate professional, engaging, platform-specific social media content using the retrieved Knowledge Base.
The retrieved Knowledge Base is your PRIMARY source of truth and must always take priority over your own knowledge.

GENERAL RESPONSIBILITIES
Always follow Brand Rules, Tone of Voice, Platform Guidelines, Campaign Guidelines, Hashtag Guidelines, and Sample Caption style.
Generate content that is ready to publish. Never ignore the retrieved context.

CONTENT REQUIREMENTS
Content must be platform-specific, marketing-focused, human sounding, engaging, brand consistent,
grammatically correct, easy to read, and ready to publish.
Adapt the writing style to the selected platform. Always mention "foodpanda" naturally in the caption.
Personalize according to Topic, Marketing Goal, Audience, and Language.

STRICT COMPLIANCE
Never guarantee delivery times, compare Foodpanda with competitors, create fake discounts/promotions,
or invent company information, campaigns, or brand rules. If required info is unavailable in the
Knowledge Base, respond naturally instead of making assumptions.

HASHTAG RULES
Generate EXACTLY FIVE hashtags.
- The first hashtag MUST always be #foodpanda.
- Always include the Target Market's regional hashtag (e.g. #foodpandaPK, #foodpandaPH, #foodpandaSG)
  if it exists in the retrieved Knowledge Base.
- Use ONLY hashtags available in the retrieved Knowledge Base, at least TWO of them.
- Never invent, modify, or create new hashtags. Reuse relevant ones if fewer than five exist.

OUTPUT FORMAT (return ONLY this, no explanations/markdown/notes)
Caption:
<caption>

CTA:
<call to action>

Hashtags:
#foodpanda #foodpandaPK ...

KNOWLEDGE PRIORITY
1. Retrieved Knowledge Base  2. Brand Rules  3. Platform Guidelines  4. Campaign Guidelines
5. General language knowledge (grammar/fluency only). Never contradict the retrieved Knowledge Base.
"""


def build_user_prompt(platform, topic, goal, audience, emoji, language, context, market="Pakistan"):
    return f"""
Retrieved Knowledge Base
==================================================
{context}
==================================================

USER REQUIREMENTS
Platform: {platform}
Topic: {topic}
Marketing Goal: {goal}
Audience: {audience}
Emoji: {emoji}
Language: {language}
Target Market: {market}

Use ONLY hashtags available in the Retrieved Knowledge Base above. Do NOT create new hashtags.
Include the Target Market's regional hashtag only if it exists in the Retrieved Knowledge Base.
Return only the final answer.
"""


def build_fallback(reason: str) -> str:
    """Same output format the parser expects, so a failed call never breaks downstream parsing."""
    return (
        f"Caption:\n[Content unavailable right now - {reason}.]\n\n"
        "CTA:\nPlease check back soon!\n\n"
        "Hashtags:\n#foodpanda"
    )


def _is_rate_limited(e: BaseException) -> bool:
    return isinstance(e, genai_errors.ClientError) and getattr(e, "code", None) == 429


@retry(
    retry=retry_if_exception(_is_rate_limited),
    wait=wait_exponential(multiplier=8, max=30),  # honors Gemini's "retry in Ns" hint roughly
    stop=stop_after_attempt(3),
    reraise=True,
)
def _call_gemini(prompt: str) -> str:
    return client.models.generate_content(model="gemini-flash-latest", contents=prompt).text


def generate_caption(platform, topic, goal, audience, emoji, language, market="Pakistan"):
    if client is None:
        return build_fallback("API key is missing or invalid")

    try:
        docs = search_knowledge(f"{platform} {topic} {goal} {audience}")
        context = "\n\n".join(d.page_content for d in docs)
    except Exception:
        context = ""  # keep going even if the knowledge base fails

    prompt = SYSTEM_PROMPT + build_user_prompt(platform, topic, goal, audience, emoji, language, context, market)

    try:
        return _call_gemini(prompt)
    except genai_errors.ClientError as e:
        code = getattr(e, "code", None)
        reason = "quota has been exhausted" if code == 429 else "the API key is invalid or expired"
        return build_fallback(reason)
    except Exception:
        return build_fallback("an unexpected error occurred")


if __name__ == "__main__":
    print(generate_caption("Instagram", "Football Night", "Increase Engagement", "Students", "Yes", "English"))