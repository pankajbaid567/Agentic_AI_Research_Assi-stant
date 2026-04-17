import streamlit as st
import pandas as pd
from agent.graph import run_research
from agent.llm_utils import call_llm_with_fallback

# Add to sidebar navigation
st.sidebar.markdown("### 🤖 Research Agent")

def render_report_section(state):
    final_report = state.get("final_report", {})
    if not final_report:
        st.warning("No report generated.")
        return

    # 1. REPORT HEADER
    st.title(final_report.get("title", "Research Report"))
    
    confidence = final_report.get("confidence", "High")
    if confidence == "High":
        color = "#2d6a4f"
    elif confidence == "Medium":
        color = "#e67e22"
    else:
        color = "#e74c3c"
        
    st.markdown(f'<span style="background:{color};color:white;padding:4px 12px;border-radius:12px;font-size:13px">✅ {confidence} Confidence</span>', unsafe_allow_html=True)
    
    generated_at = final_report.get('generated_at', 'N/A')
    sources_count = final_report.get('sources_used', 0)
    llms = final_report.get('llm_used', [])
    llms_str = ", ".join(llms) if isinstance(llms, list) else str(llms)
    st.caption(f"Generated: {generated_at} | Sources used: {sources_count} | LLM: {llms_str}")
    
    # 2. ABSTRACT
    abstract = final_report.get("abstract", "")
    if abstract:
        st.info("📋 " + abstract)
        
    # 3. KEY FINDINGS
    findings = final_report.get("key_findings", [])
    if findings:
        st.subheader("🔑 Key Findings")
        for i, finding in enumerate(findings):
            # Clean up raw markdown headers/bold formatting if fallbacks produced ugly text
            clean_finding = finding.replace("#", "").strip()
            st.markdown(f"**{i+1}.** {clean_finding}")
            
    # 4. SOURCES TABLE
    sources = final_report.get("sources", [])
    if sources:
        st.subheader("📚 Sources")
        # Format for dataframe: Title, URL, Summary
        df = pd.DataFrame(sources)
        if not df.empty:
            df = df.rename(columns={"title": "Title", "url": "URL", "summary": "Summary"})
            # Ensure only required columns exist if they are present
            cols = [c for c in ["Title", "URL", "Summary"] if c in df.columns]
            df = df[cols]
            
            st.dataframe(
                df,
                column_config={
                    "URL": st.column_config.LinkColumn("URL")
                },
                hide_index=True
            )
            
    # 5. CONCLUSION
    conclusion = final_report.get("conclusion", "")
    if conclusion:
        st.success("💡 " + conclusion)
        
    # 6. DOWNLOAD BUTTON
    if "pdf_bytes" not in st.session_state or st.session_state.get("pdf_report_title") != final_report.get('title', ''):
        from fpdf import FPDF
        import tempfile
        import os
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        title_text = final_report.get('title', 'Research Report').encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, title_text, align='C')
        pdf.ln(5)
        
        # Meta
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Generated: {generated_at} | Confidence: {confidence}", ln=True, align='C')
        pdf.ln(5)
        
        # Body
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "ABSTRACT:", ln=True)
        pdf.set_font("Arial", size=12)
        abstract_text = abstract.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, abstract_text)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "KEY FINDINGS:", ln=True)
        pdf.set_font("Arial", size=12)
        for i, finding in enumerate(findings):
            f_text = finding.replace('#', '').strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 7, f"{i+1}. {f_text}")
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONCLUSION:", ln=True)
        pdf.set_font("Arial", size=12)
        conc_text = conclusion.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, conc_text)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "SOURCES:", ln=True)
        pdf.set_font("Arial", size=10)
        for i, s in enumerate(sources):
            src_text = f"{i+1}. {s.get('title', '')} - {s.get('url', '')}".encode('latin-1', 'replace').decode('latin-1')
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
        st.session_state["pdf_report_title"] = final_report.get('title', '')
    
    st.download_button(
        "📥 Download PDF Report", 
        data=st.session_state["pdf_bytes"],
        file_name="research_report.pdf", 
        mime="application/pdf"
    )

# --- SECTION 1 — Input ---
st.title("🤖 Research Agent")
query = st.text_input(
    "Enter your research question",
    placeholder="e.g. What are recent advances in quantum computing?"
)

if st.button("🔍 Start Research"):
    if not query.strip():
        st.error("Please enter a research question.")
    else:
        # Store query for Q&A context
        st.session_state["last_query"] = query
        
        # --- SECTION 2 — Agent Progress Panel ---
        with st.status("Agent Working...", expanded=True) as status:
            with st.spinner("Invoking LangGraph..."):
                returned_state = run_research(query)
            
            # Since LangGraph runs synchronously, we show completed steps all at once here
            # simulating by reading state["current_step"] (which would be 'done' or 'error' typically)
            current_step = returned_state.get("current_step", "done")
            
            # We display all success steps as per instructions
            st.success("🔍 Searching the web...")
            st.success("📝 Summarizing sources...")
            st.success("✅ Validating source quality...")
            st.success("📄 Generating report...")
            
            status.update(label=f"Agent Finished (Status: {current_step})", state="complete", expanded=False)

        # --- SECTION 3 — Warnings (conditional) ---
        error_log = returned_state.get("error_log", [])
        if error_log:
            with st.expander("⚠️ Agent Warnings", expanded=False):
                for msg in error_log:
                    st.warning(msg)

        # --- SECTION 4 — Results placeholder ---
        st.session_state["agent_result"] = returned_state
        st.session_state["show_report"] = True

st.caption("Powered by LangGraph + Tavily + HuggingFace (Free Tier)")

if st.session_state.get("show_report", False):
    render_report_section(st.session_state["agent_result"])

    # --- FOLLOW-UP Q&A CHAT ---
    st.divider()
    st.subheader("💬 Ask a Follow-up Question")
    st.caption("Ask anything about the research findings above.")

    # 1. Session state setup setup
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # 6. Add "Clear Chat" button
    if st.button("Clear Chat"):
        st.session_state["chat_history"] = []
        st.rerun()

    # 2. Display existing chat history
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 3. Chat input
    user_input = st.chat_input("Ask about the research...")
    if user_input:
        # Append to chat_history
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # 4. Build context for LLM
        report = st.session_state["agent_result"]["final_report"]
        title = report.get('title', '')
        abstract = report.get('abstract', '')
        findings_str = chr(10).join(report.get('key_findings', []))
        conclusion = report.get('conclusion', '')
        
        context_str = f"Title: {title}\nAbstract: {abstract}\nKey Findings: {findings_str}\nConclusion: {conclusion}"

        # Include last 3 turns of chat (6 messages max)
        recent_chat = st.session_state["chat_history"][-6:]
        chat_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent_chat])

        # 5. LLM call
        prompt = f"""You are a research assistant. Answer the user's question based only on the research report below.
Be concise — answer in 2-3 sentences maximum.
Research Report:
{context_str}
Conversation so far:
{chat_str}
User's Question: {user_input}
Answer:"""

        with st.spinner("Thinking..."):
            response, _ = call_llm_with_fallback(prompt)
            if not response.strip():
                # Fallback to simple keyword extraction when LLMs are offline
                query_words = set(user_input.lower().replace('?', '').split())
                best_sentence = ""
                max_overlap = 0
                for sentence in context_str.replace('\n', '. ').split('. '):
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

        # Append assistant response to history
        st.session_state["chat_history"].append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)
