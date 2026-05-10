from crewai import Task


def get_research_task(researcher, topic: str) -> Task:
    return Task(
        description=f"""
            Research this topic: {topic}

            Do exactly 2 web searches, then stop and write your findings.
            Extract: key facts with numbers, 3-5 trends, notable sources.
            Include source URLs. Be concise — 300-400 words max.
        """,
        expected_output=(
            "A concise bullet-point list of key facts, trends, and sources. "
            "300-400 words. Include URLs."
        ),
        agent=researcher,
    )


def get_fact_check_task(fact_checker, topic: str) -> Task:
    return Task(
        description=f"""
            Review the research findings on: {topic}

            For each major claim add: [HIGH], [MEDIUM], or [LOW] confidence.
            Flag anything that seems unverified. One short paragraph summary at end.
            Do NOT search the web. Work only from what you are given.
        """,
        expected_output=(
            "The research findings with [HIGH/MEDIUM/LOW] confidence labels "
            "on each claim. One summary paragraph. 200 words max."
        ),
        agent=fact_checker,
    )


def get_analysis_task(analyst, topic: str) -> Task:
    return Task(
        description=f"""
            Analyze the research on: {topic}

            Produce exactly 4 key insights. For each insight:
            - One sentence title
            - Two sentence explanation
            - One sentence implication

            Then one short paragraph on overall patterns.
        """,
        expected_output=(
            "4 labeled insights with title, explanation, implication. "
            "One patterns paragraph. 250 words max."
        ),
        agent=analyst,
    )


def get_writing_task(writer, topic: str) -> Task:
    return Task(
        description=f"""
            Write a research report on: {topic}

            Use ONLY the research and analysis already provided to you.
            Follow this structure exactly:

            # {topic} — Research Report

            ## Executive Summary
            [3 sentences]

            ## Key Findings
            [5-6 bullet points with facts/numbers]

            ## Analysis

            ### [Insight 1]
            [2-3 sentences]

            ### [Insight 2]
            [2-3 sentences]

            ### [Insight 3]
            [2-3 sentences]

            ### [Insight 4]
            [2-3 sentences]

            ## Implications & Takeaways
            [3-4 bullet points]

            ## Sources
            [Numbered list with URLs from the research]
        """,
        expected_output=(
            "A complete markdown report following the exact structure above. "
            "600-800 words. Professional and clear."
        ),
        agent=writer,
        output_file="output/report.md",
    )