import html

import pandas as pd
import streamlit as st

from agent.graph import run_research
from agent.llm_utils import call_llm_with_fallback
from ui.streamlit_theme import inject_premium_ui

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown(
        '<p class="ra-eyebrow" style="margin:0 0 0.35rem;">Control</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### Research Agent")
    st.caption(
        "Deep research with LangGraph, web search, and structured reports — "
        "same pipeline, refined interface."
    )
    st.divider()
    theme = st.radio(
        "Theme",
        ["Dark", "Light"],
        horizontal=True,
        key="ra_appearance",
        help="Dark and light palettes; no effect on research output.",
    )
    st.divider()
    st.caption("Powered by LangGraph + Tavily + Hugging Face (free tier).")

inject_premium_ui(theme)

st.markdown(
    """
    <div class="ra-hero">
      <p class="ra-eyebrow">Agentic intelligence</p>
      <h1>Research Agent</h1>
      <p class="ra-sub">
        Ask a question. The agent searches, summarizes, validates sources, and
        delivers a report you can explore — then continue the thread in chat.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_report_section(state):
    final_report = state.get("final_report", {})
    if not final_report:
        st.warning("No report generated.")
        return

    st.title(final_report.get("title", "Research Report"))

    confidence = final_report.get("confidence", "High")
    if confidence == "High":
        badge_class = "ra-badge ra-badge--high"
    elif confidence == "Medium":
        badge_class = "ra-badge ra-badge--med"
    else:
        badge_class = "ra-badge ra-badge--low"

    st.markdown(
        f'<span class="{badge_class}">Confidence · {html.escape(str(confidence))}</span>',
        unsafe_allow_html=True,
    )

    generated_at = final_report.get("generated_at", "N/A")
    sources_count = final_report.get("sources_used", 0)
    llms = final_report.get("llm_used", [])
    llms_str = ", ".join(llms) if isinstance(llms, list) else str(llms)
    st.markdown(
        f'<p class="ra-meta">Generated: {html.escape(str(generated_at))} · '
        f"Sources: {html.escape(str(sources_count))} · "
        f'LLM: {html.escape(llms_str)}</p>',
        unsafe_allow_html=True,
    )

    abstract = final_report.get("abstract", "")
    if abstract:
        st.info("Abstract · " + abstract)

    findings = final_report.get("key_findings", [])
    if findings:
        st.markdown('<p class="ra-section-title">Key findings</p>', unsafe_allow_html=True)
        for i, finding in enumerate(findings):
            clean_finding = finding.replace("#", "").strip()
            st.markdown(f"**{i + 1}.** {clean_finding}")

    sources = final_report.get("sources", [])
    if sources:
        st.markdown('<p class="ra-section-title">Sources</p>', unsafe_allow_html=True)
        df = pd.DataFrame(sources)
        if not df.empty:
            df = df.rename(columns={"title": "Title", "url": "URL", "summary": "Summary"})
            cols = [c for c in ["Title", "URL", "Summary"] if c in df.columns]
            df = df[cols]

            st.dataframe(
                df,
                column_config={
                    "URL": st.column_config.LinkColumn("URL"),
                },
                hide_index=True,
            )

    conclusion = final_report.get("conclusion", "")
    if conclusion:
        st.success("Conclusion · " + conclusion)

    if "pdf_bytes" not in st.session_state or st.session_state.get("pdf_report_title") != final_report.get(
        "title", ""
    ):
        from fpdf import FPDF
        import os
        import tempfile

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", "B", 16)
        title_text = final_report.get("title", "Research Report").encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 10, title_text, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Generated: {generated_at} | Confidence: {confidence}", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "ABSTRACT:", ln=True)
        pdf.set_font("Arial", size=12)
        abstract_text = abstract.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, abstract_text)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "KEY FINDINGS:", ln=True)
        pdf.set_font("Arial", size=12)
        for i, finding in enumerate(findings):
            f_text = finding.replace("#", "").strip().encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, f"{i + 1}. {f_text}")
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "CONCLUSION:", ln=True)
        pdf.set_font("Arial", size=12)
        conc_text = conclusion.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, conc_text)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "SOURCES:", ln=True)
        pdf.set_font("Arial", size=10)
        for i, s in enumerate(sources):
            src_text = f"{i + 1}. {s.get('title', '')} - {s.get('url', '')}".encode(
                "latin-1", "replace"
            ).decode("latin-1")
            pdf.multi_cell(0, 6, src_text)

        pd_bytes = b""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_path = tmp.name
        try:
            pdf.output(temp_path)
            with open(temp_path, "rb") as f:
                pd_bytes = f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        st.session_state["pdf_bytes"] = pd_bytes
        st.session_state["pdf_report_title"] = final_report.get("title", "")

    st.download_button(
        "Download PDF report",
        data=st.session_state["pdf_bytes"],
        file_name="research_report.pdf",
        mime="application/pdf",
    )


query = st.text_input(
    "Research question",
    placeholder="e.g. What are recent advances in quantum computing?",
)

if st.button("Start research", type="primary"):
    if not query.strip():
        st.error("Please enter a research question.")
    else:
        st.session_state["last_query"] = query

        with st.status("Agent working…", expanded=True) as status:
            with st.spinner("Running LangGraph pipeline…"):
                returned_state = run_research(query)

            current_step = returned_state.get("current_step", "done")

            st.success("Searching the web…")
            st.success("Summarizing sources…")
            st.success("Validating source quality…")
            st.success("Generating report…")

            status.update(
                label=f"Agent finished (status: {current_step})",
                state="complete",
                expanded=False,
            )

        error_log = returned_state.get("error_log", [])
        if error_log:
            with st.expander("Agent warnings", expanded=False):
                for msg in error_log:
                    st.warning(msg)

        st.session_state["agent_result"] = returned_state
        st.session_state["show_report"] = True

if st.session_state.get("show_report", False):
    render_report_section(st.session_state["agent_result"])

    st.divider()
    st.subheader("Follow-up chat")
    st.caption("Ask anything about the research findings above.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    c_clear, _ = st.columns([1, 4])
    with c_clear:
        if st.button("Clear chat"):
            st.session_state["chat_history"] = []
            st.rerun()

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Ask about the research…")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        report = st.session_state["agent_result"]["final_report"]
        title = report.get("title", "")
        abstract = report.get("abstract", "")
        findings_str = chr(10).join(report.get("key_findings", []))
        conclusion = report.get("conclusion", "")

        context_str = f"Title: {title}\nAbstract: {abstract}\nKey Findings: {findings_str}\nConclusion: {conclusion}"

        recent_chat = st.session_state["chat_history"][-6:]
        chat_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent_chat])

        prompt = f"""You are a research assistant. Answer the user's question based only on the research report below.
Be concise — answer in 2-3 sentences maximum.
Research Report:
{context_str}
Conversation so far:
{chat_str}
User's Question: {user_input}
Answer:"""

        with st.spinner("Thinking…"):
            response, _ = call_llm_with_fallback(prompt)
            if not response.strip():
                query_words = set(user_input.lower().replace("?", "").split())
                best_sentence = ""
                max_overlap = 0
                for sentence in context_str.replace("\n", ". ").split(". "):
                    if not sentence.strip():
                        continue
                    overlap = len(set(sentence.lower().split()).intersection(query_words))
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_sentence = sentence.strip()
                if best_sentence and max_overlap > 0:
                    response = f"(Fallback Model) {best_sentence}."
                else:
                    response = "I couldn't find a specific answer in the research findings. Please try rephrasing."

        st.session_state["chat_history"].append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.write(response)
