from datetime import datetime

try:
    from agent_state import AgentState
except ImportError:
    from typing import Any
    AgentState = Any

from agent.llm_utils import call_llm_with_fallback, safe_parse_json

def report_node(state: AgentState) -> AgentState:
    validated_sources = state.get("validated_sources", [])
    validated_summaries = state.get("validated_summaries", [])
    query = state.get("query", "")
    
    # Step 1: Build context string
    context_parts = []
    for i, (src, summ) in enumerate(zip(validated_sources, validated_summaries)):
        # Handle case where summary might be a dictionary or string
        summary_text = summ.get("summary", str(summ)) if isinstance(summ, dict) else str(summ)
        title = src.get("title", "Unknown Title")
        url = src.get("url", "Unknown URL")
        
        context_parts.append(f"Source {i+1}: {title}\nURL: {url}\nSummary: {summary_text}")
        
    context = "\n\n".join(context_parts)
    
    # Truncate context to 3000 chars if too long
    if len(context) > 3000:
        context = context[:3000]

    # Step 2: LLM prompt for report
    prompt = f"""You are a research analyst. Based on the following source summaries, generate a structured research report.
Research Query: {query}

Sources:
{context}

Return ONLY a valid JSON object with this exact structure:
{{
  "abstract": "2-3 sentence overview of the main findings",
  "key_findings": ["finding 1", "finding 2", "finding 3", "finding 4", "finding 5"],
  "conclusion": "2-3 sentence synthesis and real-world implications"
}}
Do not include any text outside the JSON. No markdown. No explanation."""

    # Step 3: Parse LLM output
    llm_response, llm_name = call_llm_with_fallback(prompt)
    parsed = safe_parse_json(llm_response)
    
    if parsed is None:
        # Fallback to rule-based parsing if JSON failed
        num_sources_len = len(validated_sources)
        first_summary_text = ""
        if validated_summaries:
            first_summ = validated_summaries[0]
            first_summary_text = first_summ.get("summary", str(first_summ)) if isinstance(first_summ, dict) else str(first_summ)
            
        import textwrap
        abstract = textwrap.shorten(f"Based on {num_sources_len} sources about {query}. {first_summary_text}", width=250, placeholder="...")
        
        key_findings = []
        for s in validated_summaries[:5]:
            s_text = s.get("summary", str(s)) if isinstance(s, dict) else str(s)
            key_findings.append(textwrap.shorten(s_text, width=150, placeholder="..."))
            
        conclusion = f"Further research is recommended on the topic of {query}."
        
        parsed = {
            "abstract": abstract,
            "key_findings": key_findings,
            "conclusion": conclusion
        }
        
    # Track LLM used for report generation
    if "llm_used" not in state:
        state["llm_used"] = []
    if llm_name not in state["llm_used"]:
        state["llm_used"].append(llm_name)

    # Step 4: Assemble final_report dict
    sources_used = []
    for s, summ in zip(validated_sources, validated_summaries):
        summary_text = summ.get("summary", str(summ)) if isinstance(summ, dict) else str(summ)
        sources_used.append({
            "title": s.get("title", ""),
            "url": s.get("url", ""),
            "summary": summary_text
        })
        
    num_sources = len(validated_sources)
    if num_sources >= 4:
        confidence = "High"
    elif num_sources >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    final_report = {
        "title": f"Research Report: {query}",
        "abstract": parsed.get("abstract", ""),
        "key_findings": parsed.get("key_findings", []),
        "conclusion": parsed.get("conclusion", ""),
        "sources": sources_used,
        "generated_at": datetime.utcnow().isoformat(),
        "sources_used": num_sources,
        "confidence": confidence,
        "llm_used": state.get("llm_used", [])
    }
    
    state["final_report"] = final_report
    state["current_step"] = "done"

    return state
