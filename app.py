import streamlit as st
import sys
import os
import time
import threading
import queue
from datetime import datetime

sys.path.insert(0, "src")

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 AI Research Agent")
    st.caption("Multi-agent system built with CrewAI")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
**Agent 1 — Researcher**
Analyzes search results and extracts key facts.

**Agent 2 — Fact Checker**
Reviews findings and adds confidence scores.

**Agent 3 — Analyst**
Synthesizes findings into structured insights.

**Agent 4 — Writer**
Produces a clean, professional report in markdown.
    """)
    st.markdown("---")
    st.markdown("### Example topics")
    examples = [
        "Trends in LLM fine-tuning 2025",
        "How RAG systems are evolving",
        "State of AI agents in production",
        "Quantum computing breakthroughs 2025",
        "Open source vs closed source LLMs",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["topic_input"] = ex
            st.rerun()
    st.markdown("---")
    st.caption(
        "Built by Abdullah Chaudhary · "
        "[GitHub](https://github.com/muhammadabdullah12345) · "
        "[LinkedIn](https://linkedin.com/in/i-abdullah-chaudhary)"
    )

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "running": False,
    "done": False,
    "error": False,
    "error_msg": "",
    "result": None,
    "step": 0,
    "start_time": None,
    "msg_queue": None,   # queue.Queue lives here across reruns
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Agent steps ───────────────────────────────────────────────────────────────
AGENT_STEPS = [
    ("🔎", "Researcher",   "Analyzing search results and extracting facts..."),
    ("✅", "Fact Checker", "Verifying claims and adding confidence scores..."),
    ("🧠", "Analyst",      "Synthesizing findings into key insights..."),
    ("✍️", "Writer",       "Drafting the final report..."),
]


def render_agent_status(current_step: int, done: bool = False, error: bool = False):
    cols = st.columns(len(AGENT_STEPS))
    for i, (icon, name, desc) in enumerate(AGENT_STEPS):
        with cols[i]:
            if done and not error:
                st.success(f"{icon} **{name}**\n\nDone ✓")
            elif error and i == current_step:
                st.error(f"{icon} **{name}**\n\nFailed ✗")
            elif i < current_step:
                st.success(f"{icon} **{name}**\n\nDone ✓")
            elif i == current_step:
                st.info(f"{icon} **{name}**\n\n_{desc}_")
            else:
                st.markdown(
                    f"<div style='padding:12px;border-radius:8px;"
                    f"background:#1e1e1e;color:#666;text-align:center'>"
                    f"{icon} <b>{name}</b><br><small>Waiting...</small></div>",
                    unsafe_allow_html=True,
                )


def run_crew_thread(topic: str, q: queue.Queue):
    """
    Runs the crew in a background thread.
    Communicates ONLY via the queue — never touches st.session_state.
    Queue message format: ("step", int) | ("done", str) | ("error", str)
    """
    try:
        from crew import run_crew
        from crewai.task import Task

        original_execute = Task.execute_sync
        task_count = [0]

        def patched_execute(self, *args, **kwargs):
            q.put(("step", task_count[0]))
            task_count[0] += 1
            return original_execute(self, *args, **kwargs)

        Task.execute_sync = patched_execute

        result = run_crew(topic)

        Task.execute_sync = original_execute
        q.put(("done", str(result)))

    except Exception as e:
        try:
            from crewai.task import Task
            Task.execute_sync = original_execute
        except Exception:
            pass
        q.put(("error", str(e)))


# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown("## Generate a Research Report")
st.markdown(
    "Enter any topic and the AI agents will research, verify, analyze, "
    "and write a full report for you."
)

topic = st.text_input(
    "Research topic",
    value=st.session_state.get("topic_input", ""),
    placeholder="e.g. Latest trends in Retrieval-Augmented Generation 2025",
    key="topic_input",
    disabled=st.session_state["running"],
)

run_button = st.button(
    "▶ Run Agents",
    type="primary",
    disabled=st.session_state["running"],
)

# ── Launch crew ───────────────────────────────────────────────────────────────
if run_button and not st.session_state["running"]:
    if not topic.strip():
        st.warning("Please enter a topic to research.")
        st.stop()

    # Reset state
    st.session_state["running"] = True
    st.session_state["done"] = False
    st.session_state["error"] = False
    st.session_state["error_msg"] = ""
    st.session_state["result"] = None
    st.session_state["step"] = 0
    st.session_state["start_time"] = time.time()

    # Create queue and store in session_state so it survives reruns
    q = queue.Queue()
    st.session_state["msg_queue"] = q

    t = threading.Thread(
        target=run_crew_thread,
        args=(topic, q),
        daemon=True,
    )
    t.start()
    st.rerun()

# ── Poll queue and update state (runs every rerun while active) ───────────────
if st.session_state["running"] and st.session_state["msg_queue"] is not None:
    q = st.session_state["msg_queue"]

    # Drain all messages currently in queue
    while True:
        try:
            msg_type, msg_val = q.get_nowait()
            if msg_type == "step":
                st.session_state["step"] = msg_val
            elif msg_type == "done":
                st.session_state["result"] = msg_val
                st.session_state["done"] = True
                st.session_state["running"] = False
            elif msg_type == "error":
                st.session_state["error"] = True
                st.session_state["error_msg"] = msg_val
                st.session_state["done"] = True
                st.session_state["running"] = False
        except queue.Empty:
            break

# ── Render progress panel ─────────────────────────────────────────────────────
if st.session_state["running"] or st.session_state["done"]:
    st.markdown("---")
    st.markdown("### Agent Progress")

    current_step = min(st.session_state["step"], len(AGENT_STEPS) - 1)

    if st.session_state["done"]:
        if st.session_state["error"]:
            render_agent_status(current_step, error=True)
            err = st.session_state["error_msg"]
            if "rate_limit" in err.lower():
                st.warning(f"⏳ Rate limit hit — wait ~60s and try again.\n\n`{err[:300]}`")
            else:
                st.error(f"Something went wrong:\n\n`{err[:400]}`")
        else:
            render_agent_status(0, done=True)
            elapsed = round(time.time() - st.session_state["start_time"], 1)
            st.success(f"✅ Report generated in {elapsed}s")
    else:
        elapsed = int(time.time() - st.session_state["start_time"])
        render_agent_status(current_step)
        st.caption(f"⏱ Running for {elapsed}s")
        time.sleep(2)
        st.rerun()  # safe — only reruns while running=True

# ── Show results ──────────────────────────────────────────────────────────────
if st.session_state["done"] and not st.session_state["error"] and st.session_state["result"]:
    result = st.session_state["result"]
    topic_used = st.session_state.get("topic_input", "report")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.markdown("---")
    st.markdown("### 📥 Download Report")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="⬇ Download as Markdown",
            data=result,
            file_name=f"research_report_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        try:
            from pdf_generator import markdown_to_pdf
            pdf_path = f"output/report_{timestamp}.pdf"
            markdown_to_pdf(result, pdf_path, topic_used)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇ Download as PDF",
                    data=f.read(),
                    file_name=f"research_report_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"PDF generation failed: {str(e)}")

    st.markdown("---")
    st.markdown("## 📄 Generated Report")
    st.markdown(result)

    st.markdown("---")
    if st.button("🔄 Run Another Research"):
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.rerun()