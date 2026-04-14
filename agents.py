import re
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_website
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────

llm = ChatMistralAI(model="mistral-large-latest", temperature=0.2)


# ── Output cleaner ────────────────────────────────────────────────────────────

# Patterns that signal unwanted conversational filler
_FILLER_PATTERNS = re.compile(
    r"(would you like|let me know|feel free|i hope|is there anything|"
    r"please note|do you want|shall i|if you need|i can also|"
    r"happy to help|here to help|as an ai|as a language model)",
    re.IGNORECASE,
)


def clean_output(text: str) -> str:
    """
    Remove conversational filler sentences from LLM output.
    Splits on sentence boundaries and drops any sentence containing filler phrases.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    cleaned = [s for s in sentences if not _FILLER_PATTERNS.search(s)]
    return " ".join(cleaned).strip()


# ── Search Agent (direct tool call) ──────────────────────────────────────────

def run_search_agent(topic: str) -> str:
    """
    Directly invokes the web_search tool — no LLM wrapper.
    Returns clean structured Markdown search results.
    """
    return web_search.invoke(topic)


# ── Reader Agent (direct tool calls) ─────────────────────────────────────────

def run_reader_agent(urls: list[str]) -> str:
    """
    Directly scrapes each URL without an LLM wrapper.
    Returns combined Markdown content from all scraped pages.
    """
    if not urls:
        return "_No URLs available to scrape._"

    sections = []
    for url in urls[:3]:  # cap at 3 to stay within token budget
        result = scrape_website.invoke(url)
        sections.append(result)

    return "\n\n---\n\n".join(sections)


# ── Writer Chain ──────────────────────────────────────────────────────────────

_WRITER_SYSTEM = """\
You are a professional research analyst writing structured research reports.

ABSOLUTE RULES — violating any of these is unacceptable:
- NEVER add questions or suggestions at the end.
- NEVER write "Would you like...", "Let me know...", "Feel free to...", or any similar phrase.
- NEVER add conversational openers or closers.
- NEVER write more than 4 lines in a single paragraph.
- Output ONLY the report — nothing before or after it.
- Use Markdown formatting: ## headings, bullet points (- ), and **bold** for emphasis.
- Keep language formal, concise, and factual.
"""

_WRITER_HUMAN = """\
Write a structured research report on the topic below using the provided research notes.

**Topic:** {topic}

**Research Notes:**
{research}

---

Use EXACTLY this structure — no additions, no omissions:

## Executive Summary
3–4 sentences. What this topic is and why it matters right now.

## Key Findings
- Bullet point per finding (6–10 bullets)
- Each bullet = one concrete fact or data point
- No vague generalizations

## Detailed Analysis

### [Sub-topic 1 — derive from research]
2–3 short paragraphs max.

### [Sub-topic 2 — derive from research]
2–3 short paragraphs max.

### [Sub-topic 3 — derive from research]
2–3 short paragraphs max.

## Conclusion
3–4 sentences. Synthesis of findings and implications.

## Sources Referenced
List the source URLs from the research notes as a Markdown list.

---
OUTPUT THE REPORT ONLY. NO OTHER TEXT.
"""

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", _WRITER_SYSTEM),
    ("human",  _WRITER_HUMAN),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ── Critic Chain ──────────────────────────────────────────────────────────────

_CRITIC_SYSTEM = """\
You are a senior editorial critic evaluating research reports.
Be rigorous, specific, and objective. No flattery. No filler.

RULES:
- Output ONLY the structured review below — nothing else.
- Every point must be specific and actionable, not generic.
- Do NOT add conversational lines or suggestions to "reach out".
"""

_CRITIC_HUMAN = """\
Critically evaluate the research report below.

**Report:**
{report}

---

Respond using EXACTLY this format:

## Quality Score

**Overall: X / 10**

| Dimension       | Score | Notes                          |
|-----------------|-------|--------------------------------|
| Accuracy        | X/10  | Brief note                     |
| Depth           | X/10  | Brief note                     |
| Clarity         | X/10  | Brief note                     |
| Structure       | X/10  | Brief note                     |
| Objectivity     | X/10  | Brief note                     |

## Strengths
- (specific strength 1)
- (specific strength 2)
- (specific strength 3)

## Weaknesses
- (specific weakness 1)
- (specific weakness 2)
- (specific weakness 3)

## Verdict
One paragraph (3–4 sentences). Is this publication-ready? What is the single most important improvement needed?

---
OUTPUT THE REVIEW ONLY. NO OTHER TEXT.
"""

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", _CRITIC_SYSTEM),
    ("human",  _CRITIC_HUMAN),
])

critic_chain = critic_prompt | llm | StrOutputParser()