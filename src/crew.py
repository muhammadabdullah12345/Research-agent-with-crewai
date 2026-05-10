from crewai import Crew, Process
from dotenv import load_dotenv
from agents import get_researcher, get_analyst, get_fact_checker, get_writer
from tasks import (
    get_research_task,
    get_fact_check_task,
    get_analysis_task,
    get_writing_task,
)
import os
import time

load_dotenv()


def run_crew(topic: str) -> str:
    os.makedirs("output", exist_ok=True)

    researcher = get_researcher()
    fact_checker = get_fact_checker()
    analyst = get_analyst()
    writer = get_writer()

    research_task = get_research_task(researcher, topic)
    fact_check_task = get_fact_check_task(fact_checker, topic)
    analysis_task = get_analysis_task(analyst, topic)
    writing_task = get_writing_task(writer, topic)

    fact_check_task.context = [research_task]
    analysis_task.context = [research_task, fact_check_task]
    writing_task.context = [research_task, fact_check_task, analysis_task]

    crew = Crew(
        agents=[researcher, fact_checker, analyst, writer],
        tasks=[research_task, fact_check_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str and attempt < max_retries - 1:
                # Extract wait time from error message if present
                wait_time = 60
                if "Please try again in" in error_str:
                    try:
                        wait_str = error_str.split("Please try again in")[1].split("s.")[0].strip()
                        wait_time = int(float(wait_str)) + 5
                    except Exception:
                        wait_time = 60
                print(f"Rate limit hit. Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e

    raise RuntimeError("Max retries exceeded due to rate limiting.")