import sys
try:
    import pkg_resources
except ModuleNotFoundError:
    import types
    _pkg = types.ModuleType("pkg_resources")
    _pkg.require = lambda *a, **k: None
    _pkg.get_distribution = lambda *a, **k: None
    _pkg.working_set = []
    _pkg.DistributionNotFound = Exception
    _pkg.VersionConflict = Exception
    sys.modules["pkg_resources"] = _pkg

from crewai import Agent, LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm_fast = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY"),
)

llm_strong = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.4,
    api_key=os.getenv("GEMINI_API_KEY"),
)
# llm_fast = LLM(
#     model="openrouter/google/gemini-2.0-flash-exp:free",
#     temperature=0.3,
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
# )

# llm_strong = LLM(
#     model="openrouter/google/gemini-2.0-flash-exp:free",
#     temperature=0.4,
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
# )

def get_researcher():
    return Agent(
        role="Senior Research Analyst",
        goal="Search the web exactly twice and return a concise findings summary",
        backstory=(
            "You are an efficient researcher. You run exactly 2 targeted searches, "
            "extract the most important facts from the results, and stop. "
            "You do not search more than twice. You write a clear, concise summary."
        ),
        tools=[search_tool],
        llm=llm_fast,
        verbose=True,
        allow_delegation=False,
        max_iter=2,  # hard cap: search twice then conclude
    )


def get_fact_checker():
    return Agent(
        role="Fact Checker",
        goal="Review research findings and annotate confidence levels",
        backstory=(
            "You review research findings and add HIGH/MEDIUM/LOW confidence "
            "labels to each claim. You work only from what you are given. "
            "You do not search the web."
        ),
        llm=llm_fast,
        verbose=True,
        allow_delegation=False,
        max_iter=1,  # no tools, one pass is enough
    )


def get_analyst():
    return Agent(
        role="Content Analyst",
        goal="Extract 4 key insights from the research in a structured format",
        backstory=(
            "You read research findings and produce exactly 4 key insights "
            "with patterns and implications. You are concise and structured."
        ),
        llm=llm_fast,
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )


def get_writer():
    return Agent(
        role="Technical Report Writer",
        goal="Write a professional markdown research report from the analysis provided",
        backstory=(
            "You write clean, professional research reports in markdown. "
            "You use the analysis given to you and do not invent new research."
        ),
        llm=llm_strong,
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )