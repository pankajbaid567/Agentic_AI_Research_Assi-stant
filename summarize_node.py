try:
    from agent_state import AgentState
except ImportError:
    from typing import Any
    AgentState = Any

from agent.llm_utils import call_llm_with_fallback

def summarize_node(state: AgentState) -> AgentState:
    # Initialize lists in state if they don't exist
    if "summaries" not in state:
        state["summaries"] = []
    if "llm_used" not in state:
        state["llm_used"] = []
    if "error_log" not in state:
        state["error_log"] = []
        
    search_results = state.get("search_results", [])
    
    for result in search_results:
        try:
            content = result.get("content", "")
            # Truncate to first 1500 chars to avoid token limit
            truncated_content = content[:1500]
            
            prompt = f"""Summarize the following research content in exactly 3-4 sentences. Focus only on key findings, data, or claims. Be factual and concise. Content: {truncated_content} Summary:"""
            
            summary_text, llm_used = call_llm_with_fallback(prompt)
            
            if not summary_text:
                try:
                    from milestone1.summarizer import ExtractiveSummarizer
                    summarizer = ExtractiveSummarizer()
                    summary_text = summarizer.summarize(truncated_content)
                except ImportError:
                    import textwrap
                    summary_text = textwrap.shorten(truncated_content, width=300, placeholder="...")
            
            # Append summary dict
            state["summaries"].append({
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "summary": summary_text
            })
            
            # Track llm_used
            if llm_used not in state["llm_used"]:
                state["llm_used"].append(llm_used)
                
        except Exception as e:
            # Log any per-source failures
            error_msg = f"Summarization error for {result.get('url', 'unknown')}: {str(e)}"
            state["error_log"].append(error_msg)

    # Update step at the end
    state["current_step"] = "summarization_complete"
    
    return state
