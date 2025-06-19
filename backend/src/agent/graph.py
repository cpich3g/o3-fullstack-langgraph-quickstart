import os
import json
import tempfile
import subprocess
import sys
import io
import base64
from typing import Dict, Any, List
from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from openai import AzureOpenAI

# Azure Container Apps dynamic sessions import
try:
    from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
    AZURE_SESSIONS_AVAILABLE = True
except ImportError:
    SessionsPythonREPLTool = None
    AZURE_SESSIONS_AVAILABLE = False

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
    CodeGeneratorState,
    CodeExecutorState,
    ReportGeneratorState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
    code_generator_instructions,
    code_executor_instructions,
    report_generator_instructions,
)
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)
from agent.web_research import enhance_ai_research_with_real_data

load_dotenv()

if os.getenv("AZURE_OPENAI_API_KEY") is None:
    raise ValueError("AZURE_OPENAI_API_KEY is not set")

# Azure OpenAI client
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Global Azure Sessions tool instance
_azure_sessions_tool = None

def _is_actual_python_code(code_content: str) -> bool:
    """Validate that the provided content is actual executable Python code."""
    if not code_content or not code_content.strip():
        return False
    
    # Check for common Python indicators
    python_indicators = [
        'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
        'print(', '=', 'pandas', 'numpy', 'matplotlib', 'plt.', 'df.',
        'data.', 'pd.', 'np.', 'sns.', 'seaborn'
    ]
    
    # Remove comments and strings to avoid false positives
    lines = code_content.split('\n')
    code_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            code_lines.append(line)
    
    if not code_lines:
        return False
    
    # Check if any line contains Python indicators
    has_python_indicators = any(
        any(indicator in line for indicator in python_indicators)
        for line in code_lines
    )
    
    # Basic syntax validation - try to compile (but don't execute)
    try:
        compile(code_content, '<string>', 'exec')
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False
    except Exception:
        # Other compilation errors still indicate it's Python-like
        syntax_valid = True
    
    return has_python_indicators and syntax_valid

def get_azure_sessions_tool(pool_management_endpoint: str = None):
    """Get or create Azure Container Apps dynamic sessions tool."""
    global _azure_sessions_tool
    
    if not AZURE_SESSIONS_AVAILABLE:
        raise ImportError("langchain-azure-dynamic-sessions package not available")
    
    if pool_management_endpoint is None:
        pool_management_endpoint = os.getenv("AZURE_POOL_MANAGEMENT_ENDPOINT")
    
    if not pool_management_endpoint:
        raise ValueError("Azure Pool Management Endpoint not configured. Set AZURE_POOL_MANAGEMENT_ENDPOINT environment variable.")
    
    if _azure_sessions_tool is None:
        try:
            # Try to create the tool without explicit credentials first (for public endpoints)
            _azure_sessions_tool = SessionsPythonREPLTool(
                pool_management_endpoint=pool_management_endpoint
            )
            # Test the connection with a simple operation
            test_result = _azure_sessions_tool.execute("print('Connection test successful')")
            print(f"✅ Azure Container Apps sessions connected successfully")
            
        except Exception as auth_error:
            print(f"⚠️  Azure sessions authentication failed: {str(auth_error)}")
            print("   This may be normal for public endpoints. Trying without authentication...")
            
            # For public endpoints that don't require authentication,
            # we might need to handle this differently
            try:
                # Try creating with minimal configuration
                _azure_sessions_tool = SessionsPythonREPLTool(
                    pool_management_endpoint=pool_management_endpoint
                )
                print(f"✅ Azure Container Apps sessions initialized (public endpoint)")
            except Exception as e:
                print(f"❌ Failed to initialize Azure sessions: {str(e)}")
                raise e
    
    return _azure_sessions_tool


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates a search queries based on the User's question using Azure OpenAI."""
    configurable = Configuration.from_runnable_config(config)
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )

    completion = openai_client.chat.completions.create(
        model=configurable.query_generator_model,
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=1.0,
        max_tokens=500,
    )
    # Parse output (assuming output is a JSON list of queries)
    import json
    try:
        queries = json.loads(completion.choices[0].message.content)
    except Exception:
        queries = [completion.choices[0].message.content]
    return {"query_list": queries }


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


async def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using Azure OpenAI with optional SerpAPI enhancement."""
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )
    
    completion = openai_client.chat.completions.create(
        model=configurable.query_generator_model,
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=0,
        max_tokens=1024,
    )
    ai_generated_text = completion.choices[0].message.content
      # Enhance with real web data if search engines are available and enabled
    sources_gathered = []
    if configurable.use_web_research:
        try:
            enhanced_result = await enhance_ai_research_with_real_data(
                state["search_query"], 
                ai_generated_text,
                search_engine=configurable.search_engine
            )
            final_text = enhanced_result["enhanced_content"]
            
            # Convert sources to the expected format
            for source in enhanced_result["sources"]:
                sources_gathered.append({
                    "label": source["title"][:50] + "..." if len(source["title"]) > 50 else source["title"],
                    "short_url": source["url"],
                    "value": source["url"],
                    "snippet": source["snippet"],
                    "scraped_successfully": source.get("scraped_successfully", False)
                })
        except Exception as e:
            print(f"Error enhancing web research: {e}")
            final_text = ai_generated_text
    else:
        final_text = ai_generated_text
    
    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [final_text],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries using Azure OpenAI."""
    configurable = Configuration.from_runnable_config(config)
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = configurable.reasoning_model
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    completion = openai_client.chat.completions.create(
        model=reasoning_model,
        messages=[{"role": "user", "content": formatted_prompt}],
        # max_tokens=100000,
        # temperature=0.7,
        reasoning_effort="high",
    )
    import json
    try:
        result = json.loads(completion.choices[0].message.content)
    except Exception:
        result = {
            "is_sufficient": False,
            "knowledge_gap": "",
            "follow_up_queries": [],
        }
    return {
        "is_sufficient": result.get("is_sufficient", False),
        "knowledge_gap": result.get("knowledge_gap", ""),
        "follow_up_queries": result.get("follow_up_queries", []),
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    
    if (state["is_sufficient"] or 
        state["research_loop_count"] >= max_research_loops or
        (not state["is_sufficient"] and not state["follow_up_queries"])):
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary and determines if code analysis is needed."""
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = configurable.reasoning_model
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )
    completion = openai_client.chat.completions.create(
        model=reasoning_model,
        messages=[{"role": "user", "content": formatted_prompt}],
        # temperature=0.4,
        reasoning_effort="high",
    )
    content = completion.choices[0].message.content
    
    # Parse the response to extract code analysis decision
    code_analysis_needed = False
    analysis_rationale = ""
    analysis_type = "none"
    
    if "CODE_ANALYSIS_NEEDED:" in content:
        lines = content.split('\n')
        main_content = []
        
        for line in lines:
            if line.strip().startswith("CODE_ANALYSIS_NEEDED:"):
                code_analysis_needed = "true" in line.lower()
            elif line.strip().startswith("ANALYSIS_RATIONALE:"):
                analysis_rationale = line.replace("ANALYSIS_RATIONALE:", "").strip()
            elif line.strip().startswith("ANALYSIS_TYPE:"):
                analysis_type = line.replace("ANALYSIS_TYPE:", "").strip()
            elif not line.strip().startswith("CODE_ANALYSIS") and not line.strip() == "---":
                main_content.append(line)
        
        # Clean content (remove the analysis decision markers)
        content = '\n'.join(main_content).strip()
    
    print(f"🤖 Finalize Answer - Code Analysis Decision: {'✅ Needed' if code_analysis_needed else '❌ Not needed'}")
    if analysis_rationale:
        print(f"   Rationale: {analysis_rationale}")
    if analysis_type != "none":
        print(f"   Analysis Type: {analysis_type}")
    
    unique_sources = []
    for source in state["sources_gathered"]:
        if source.get("short_url") and source["short_url"] in content:
            content = content.replace(source["short_url"], source["value"])
            unique_sources.append(source)
      # Create research steps for frontend display (metadata only, no message)
    research_steps = []
    search_queries = state.get("search_query", [])
    
    for i, query in enumerate(search_queries, 1):
        research_steps.append({
            "step": i,
            "type": "search",
            "description": f"Searched for: {query}",
            "status": "completed"
        })
    
    # Add analysis step
    if search_queries:
        research_steps.append({
            "step": len(search_queries) + 1,
            "type": "analysis",
            "description": "Analyzed and synthesized information from sources",
            "status": "completed"
        })
    
    # Store metadata for the final report (no message creation here)
    structured_data = {
        "sources": unique_sources,
        "research_summary": {
            "total_queries": len(state.get("search_query", [])),
            "research_loops": state.get("research_loop_count", 0),
            "sources_found": len(unique_sources),
            "research_steps": research_steps
        }
    }
    
    return {
        # Don't create a message here - let report_generator handle final output
        "sources_gathered": unique_sources,
        "code_analysis_needed": code_analysis_needed,
        "analysis_rationale": analysis_rationale,
        "analysis_type": analysis_type,
        "finalize_metadata": structured_data,  # Store for report_generator
        "finalized_content": content,  # Store content for report_generator
    }


def code_generator(state: OverallState, config: RunnableConfig) -> OverallState:
    """LangGraph node that generates Python code based on finalized analysis requirements."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.enable_code_interpreter:
        print("🚫 Code interpreter disabled in configuration")
        return {
            "code_analysis_needed": False,
            "generated_code": "",
        }
    
    # Check if code analysis was determined to be needed by finalize_answer
    if not state.get("code_analysis_needed", False):
        print("🚫 Code analysis not needed according to finalize_answer decision")
        return {
            "code_analysis_needed": False,
            "generated_code": "",
        }
    
    # Get research content and analysis requirements
    research_content = "\n".join(state["web_research_result"])
    research_topic = get_research_topic(state["messages"])
    analysis_type = state.get("analysis_type", "none")
    analysis_rationale = state.get("analysis_rationale", "")
    
    if not research_content.strip():
        print("⚠️  No research content available for code generation")
        return {
            "code_analysis_needed": False,
            "generated_code": "",
        }
    
    print(f"🤖 Generating {analysis_type} code based on finalize_answer decision...")
    
    # Use Azure OpenAI to generate the specific code requested
    formatted_prompt = code_generator_instructions.format(
        research_topic=research_topic,
        research_content=research_content,
        analysis_type=analysis_type,
        analysis_rationale=analysis_rationale,
    )
    
    try:
        completion = openai_client.chat.completions.create(
            model=configurable.code_interpreter_model,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.1,
            max_tokens=2000,        )
        
        python_code = completion.choices[0].message.content.strip()
        
        # Strip markdown formatting if present
        if "```python" in python_code:
            # Extract code between ```python and ```
            start_marker = "```python"
            end_marker = "```"
            start_idx = python_code.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = python_code.find(end_marker, start_idx)
                if end_idx != -1:
                    python_code = python_code[start_idx:end_idx].strip()
        elif "```" in python_code:
            # Handle generic code blocks
            lines = python_code.split('\n')
            in_code_block = False
            code_lines = []
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                elif in_code_block or not any(line.strip().startswith(marker) for marker in ['```']):
                    if not line.strip().startswith('```'):
                        code_lines.append(line)
            if code_lines:
                python_code = '\n'.join(code_lines).strip()
        
        # The new prompt returns plain Python code, so validate it directly
        if python_code and _is_actual_python_code(python_code):
            print(f"📝 Generated {len(python_code)} characters of {analysis_type} Python code")
            return {
                "code_analysis_needed": True,
                "generated_code": python_code,
            }
        else:
            print("⚠️  Generated content is not valid Python code")
            return {
                "code_analysis_needed": False,
                "generated_code": "",
            }
        
    except Exception as e:
        print(f"❌ Code generation failed: {str(e)}")
        return {
            "code_analysis_needed": False,
            "generated_code": "",
        }


def code_executor(state: OverallState, config: RunnableConfig) -> OverallState:
    """LangGraph node that executes Python code using Azure Container Apps dynamic sessions."""
    configurable = Configuration.from_runnable_config(config)
    
    # Check if we have code to execute
    python_code = state.get("generated_code", "").strip()
    if not python_code:
        print("📝 No code to execute")
        return {"code_analysis_results": ["No code to execute"]}
      # CRITICAL VALIDATION: Ensure only actual Python code gets sent to sandbox
    if not _is_actual_python_code(python_code):
        print("⚠️  Generated content is not valid Python code, skipping execution")
        return {"code_analysis_results": ["Generated content is not executable Python code"]}
    
    print(f"🔬 Sending Python code to sandbox for execution ({len(python_code)} characters)")
    print(f"   Code preview: {python_code[:200]}{'...' if len(python_code) > 200 else ''}")
    
    # Check if code is safe before execution
    if not _is_safe_code(python_code):
        print("❌ Code safety check failed - code contains potentially unsafe operations")
        error_result = {
            "code_executed": python_code,
            "results": "",
            "visualizations": [],
            "insights": "Code contains potentially unsafe operations",
            "errors": "Code safety check failed",
            "execution_method": "subprocess_blocked"
        }
        return {"code_analysis_results": [error_result]}
    try:
        # Try to use Azure Container Apps dynamic sessions first
        if configurable.use_azure_sessions and AZURE_SESSIONS_AVAILABLE:
            return _execute_code_with_azure_sessions(python_code, configurable)
        else:
            # Fallback to subprocess execution
            return _execute_code_with_subprocess(python_code, configurable)
    
    except Exception as e:
        error_result = {
            "code_executed": python_code,
            "results": "",
            "visualizations": [],
            "insights": f"Code execution failed: {str(e)}",
            "errors": str(e),
            "execution_method": "failed"
        }
        return {"code_analysis_results": [error_result]}


def _execute_code_with_azure_sessions(python_code: str, configurable) -> OverallState:
    """Execute Python code using Azure Container Apps dynamic sessions."""
    try:
        # Get Azure sessions tool
        pool_endpoint = configurable.pool_management_endpoint or os.getenv("AZURE_POOL_MANAGEMENT_ENDPOINT")
        
        if not pool_endpoint:
            print("⚠️  No Azure Container Apps sessions endpoint configured, falling back to subprocess execution")
            return _execute_code_with_subprocess(python_code, configurable)
        
        print(f"🔗 Connecting to Azure Container Apps sessions...")
        
        try:
            sessions_tool = get_azure_sessions_tool(pool_endpoint)
        except Exception as connection_error:
            print(f"⚠️  Azure sessions connection failed: {str(connection_error)}")
            print("   Falling back to subprocess execution")
            return _execute_code_with_subprocess(python_code, configurable)
        
        # Execute the code
        print(f"🚀 Executing code in Azure Container Apps sandbox...")
        
        try:
            execution_result = sessions_tool.execute(python_code)
            print(f"✅ Code execution completed successfully")
        except Exception as exec_error:
            error_msg = str(exec_error)
            print(f"❌ Azure sessions execution failed: {error_msg}")
            
            # Check if it's an authentication error and suggest fallback
            if any(keyword in error_msg.lower() for keyword in ['credential', 'authentication', 'token', 'auth']):
                print("   This appears to be an authentication issue.")
                print("   Falling back to subprocess execution...")
                return _execute_code_with_subprocess(python_code, configurable)
            else:
                # For other execution errors, still try fallback
                print("   Falling back to subprocess execution...")
                return _execute_code_with_subprocess(python_code, configurable)
        
        # Process the result
        analysis_result = _process_azure_sessions_result(execution_result, python_code)
        
        return {"code_analysis_results": [analysis_result]}
        
    except Exception as e:
        print(f"❌ Unexpected error in Azure sessions execution: {str(e)}")
        print("   Falling back to subprocess execution...")
        return _execute_code_with_subprocess(python_code, configurable)


def _execute_code_with_subprocess(python_code: str, configurable) -> OverallState:
    """Execute Python code using subprocess fallback."""
    
    print(f"🔄 Executing code using subprocess fallback...")
    
    try:
        # Execute the code
        execution_result = _execute_python_code(python_code)
        
        analysis_result = {
            "code_executed": python_code,
            "execution_method": "subprocess_fallback",
            "visualizations": execution_result.get("visualizations", []),
            "errors": execution_result.get("error", ""),
            "stdout": execution_result.get("output", ""),
        }
        
        if execution_result.get("success"):
            analysis_result["results"] = execution_result["output"]
            if execution_result.get("visualizations"):
                analysis_result["insights"] = f"Code executed successfully. Generated {len(execution_result['visualizations'])} visualization(s)."
            else:
                analysis_result["insights"] = "Code executed successfully using subprocess fallback"
        else:
            analysis_result["results"] = ""
            analysis_result["insights"] = f"Code execution failed: {execution_result.get('error', 'Unknown error')}"
        
        return {"code_analysis_results": [analysis_result]}
        
    except Exception as e:
        error_result = {
            "code_executed": python_code,
            "results": "",
            "visualizations": [],
            "insights": "",
            "errors": f"Subprocess execution error: {str(e)}",
            "execution_method": "subprocess_failed"
        }
        return {"code_analysis_results": [error_result]}


# Helper function to generate analysis code (legacy, now replaced by code_generator node)
def _generate_analysis_code_legacy(research_content: str, research_topic: str, configurable) -> str:
    """Legacy function - now replaced by dedicated code_generator node."""
    # This function is kept for backward compatibility but should not be used
    # The code_generator node now handles code generation
    return ""


def _process_azure_sessions_result(execution_result: Dict[str, Any], code_executed: str) -> Dict[str, Any]:
    """Process the result from Azure Container Apps dynamic sessions execution."""
    
    analysis_result = {
        "code_executed": code_executed,
        "execution_method": "azure_sessions",
        "execution_time_ms": execution_result.get("executionTimeInMilliseconds", 0),
        "status": execution_result.get("status", "Unknown"),
        "errors": execution_result.get("stderr", ""),
        "stdout": execution_result.get("stdout", ""),
        "visualizations": []
    }
    
    # Process the result based on its type
    result_data = execution_result.get("result")
    
    if isinstance(result_data, dict) and result_data.get("type") == "image":
        # Handle image results (charts/visualizations)
        analysis_result["visualizations"].append({
            "type": result_data.get("type"),
            "format": result_data.get("format"),
            "base64_data": result_data.get("base64_data"),
            "description": "Generated visualization from analysis"
        })
        analysis_result["results"] = "Visualization generated successfully"
        analysis_result["insights"] = "Data visualization created showing analysis results"
        
    elif isinstance(result_data, (str, int, float, list, dict)):
        # Handle text/numeric results
        analysis_result["results"] = str(result_data)
        analysis_result["insights"] = f"Analysis completed with result: {str(result_data)}"
        
    else:
        analysis_result["results"] = str(result_data) if result_data else "Analysis completed"
        analysis_result["insights"] = "Code executed successfully"
    
    # Combine stdout for additional insights if available
    if analysis_result["stdout"]:
        analysis_result["insights"] += f"\n\nAdditional output:\n{analysis_result['stdout']}"
    
    return analysis_result


# Legacy functions removed - functionality now split between code_generator and code_executor nodes


def report_generator(state: OverallState, config: RunnableConfig) -> OverallState:
    """LangGraph node that generates a clean, user-friendly research report using Azure OpenAI."""
    configurable = Configuration.from_runnable_config(config)
    
    # Check if we should use the finalized content directly (when report generation is disabled)
    if not configurable.enable_report_generator:
        finalized_content = state.get("finalized_content", "")
        finalize_metadata = state.get("finalize_metadata", {})
        
        if finalized_content:
            return {
                "final_report": finalized_content,
                "messages": [AIMessage(content=finalized_content, additional_kwargs=finalize_metadata)],
            }
        else:
            return {"final_report": "Report generation failed - no content available"}
    
    research_topic = get_research_topic(state["messages"])
    current_date = get_current_date()
    
    # Prepare research data (summarized)
    research_summary = {
        "key_findings": state.get("web_research_result", []),
        "total_sources": len(state.get("sources_gathered", [])),
        "research_completeness": "comprehensive" if state.get("research_loop_count", 0) > 1 else "focused"
    }
    
    # Prepare code analysis results (clean summary)
    code_analysis_summary = []
    code_results = state.get("code_analysis_results", [])
    has_visualizations = False
    
    for result in code_results:
        if isinstance(result, dict):
            # Check for visualizations
            if result.get("visualizations") or "plt.show()" in result.get("code_executed", ""):
                has_visualizations = True
            
            # Extract insights without showing raw code
            summary = {
                "type": "computational_analysis",
                "insights": result.get("insights", ""),
                "key_results": result.get("results", ""),
                "has_visualization": bool(result.get("visualizations"))
            }
            code_analysis_summary.append(summary)
    
    # Prepare clean sources (just the key ones)
    key_sources = []
    for source in state.get("sources_gathered", [])[:8]:  # Limit to top 8 sources
        if source.get("scraped_successfully", False):
            key_sources.append({
                "title": source.get("label", ""),
                "url": source.get("value", ""),
                "relevance": "high" if source.get("snippet") else "medium"
            })
    
    formatted_prompt = report_generator_instructions.format(
        research_topic=research_topic,
        research_data=json.dumps(research_summary, indent=2),
        code_results=json.dumps(code_analysis_summary, indent=2),
        sources=json.dumps(key_sources, indent=2),
        current_date=current_date
    )
    
    try:
        completion = openai_client.chat.completions.create(
            model=configurable.report_generator_model,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
            max_tokens=3000,  # Reduced for cleaner output
        )
        
        report_content = completion.choices[0].message.content
        
        # If there were visualizations created, add a note about them
        if has_visualizations:
            visualization_note = "\n\n*Note: Data visualizations have been generated to illustrate key findings.*"
            report_content += visualization_note        # Create combined structured data for the UI
        finalize_metadata = state.get("finalize_metadata", {})
        ui_metadata = {
            # Merge with existing metadata from finalize_answer
            **finalize_metadata,
            # Add report-specific metadata
            "sources": state.get("sources_gathered", []),
            "has_visualizations": has_visualizations,
            "analysis_performed": bool(code_analysis_summary),
            "report_type": "user_friendly",
            "code_analysis_results": code_results  # Include full code results for visualization access
        }
        
        return {
            "final_report": report_content,
            "messages": [AIMessage(content=report_content, additional_kwargs=ui_metadata)],
        }
        
    except Exception as e:
        # Fallback to a simple response
        fallback_content = f"I've completed the research on {research_topic}. "
        
        # Add key findings if available
        if state.get("web_research_result"):
            fallback_content += "Here are the key findings:\n\n"
            for finding in state.get("web_research_result", [])[:2]:
                fallback_content += f"• {finding[:200]}...\n"
        
        # Add code insights if available
        if code_results and any(r.get("insights") for r in code_results):
            fallback_content += "\nAdditional analysis reveals:\n"
            for result in code_results[:1]:
                if result.get("insights"):
                    fallback_content += f"• {result['insights'][:200]}...\n"
        
        return {
            "final_report": fallback_content,
            "messages": [AIMessage(content=f"Research completed with some limitations: {str(e)}\n\n{fallback_content}")]
        }


def _is_safe_code(code: str) -> bool:
    """Check if Python code is safe to execute (basic safety check)."""
    # More restrictive list focusing on truly dangerous operations
    dangerous_patterns = [
        "__import__", "exec(", "eval(", 
        "subprocess.call", "subprocess.run", "subprocess.Popen", "subprocess.check_output",
        "os.system", "os.popen", "os.spawn", "os.execv", "os.execl",
        "open(", "file(", "input(", "raw_input(",
        "exit(", "quit(", "sys.exit",
        "rmdir", "shutil.rmtree", "os.remove", "os.unlink", "os.rmdir",
        "socket.socket", "urllib.request", "requests.get", "requests.post", "requests.put",
        "pickle.load", "marshal.load", "compile(",
        "globals(", "locals(", "vars(", "dir(",
        "getattr(", "setattr(", "delattr(", "hasattr(",
        "__builtins__", "__globals__", "__locals__"
    ]
    
    code_lower = code.lower()
    
    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            print(f"⚠️  Code safety check failed: detected dangerous pattern '{pattern}'")
            return False
    
    # Additional check for file system operations
    if any(keyword in code_lower for keyword in ["write(", "writelines(", "w'", 'w"']):
        # Allow only in-memory operations or safe matplotlib/plot saving
        if not any(safe_write in code_lower for safe_write in ["stringio", "bytesio", "savefig", "to_csv", "to_json"]):
            print("⚠️  Code safety check failed: detected file write operations")
            return False
    
    return True


def _execute_python_code(code: str) -> Dict[str, Any]:
    """Safely execute Python code in a restricted environment and capture visualizations."""
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Add common imports for data analysis and visualization capture
            safe_code = """
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import io
import base64
import os

# Function to capture and save plots as base64
def save_plot_as_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()  # Close the figure to free memory
    return img_base64

# Track if any plots were created
_plots_created = []

# Override plt.show() to capture plots
original_show = plt.show
def custom_show():
    if plt.get_fignums():  # Check if any figures exist
        img_data = save_plot_as_base64()
        _plots_created.append(img_data)
        print(f"VISUALIZATION_CAPTURED:{img_data}")
    else:
        original_show()

plt.show = custom_show

""" + code + """

# Capture any remaining plots that weren't explicitly shown
if plt.get_fignums():
    img_data = save_plot_as_base64()
    _plots_created.append(img_data)
    print(f"VISUALIZATION_CAPTURED:{img_data}")
"""
            f.write(safe_code)
            temp_file = f.name
        
        # Execute the code with timeout
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Clean up
        os.unlink(temp_file)
        
        # Extract visualizations from output
        visualizations = []
        output_lines = []
        
        for line in result.stdout.split('\n'):
            if line.startswith('VISUALIZATION_CAPTURED:'):
                img_data = line.replace('VISUALIZATION_CAPTURED:', '')
                visualizations.append({
                    "type": "image",
                    "format": "png",
                    "base64_data": img_data,
                    "description": "Generated visualization"
                })
            else:
                output_lines.append(line)
        
        clean_output = '\n'.join(output_lines).strip()
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": clean_output,
                "error": result.stderr if result.stderr else "",
                "visualizations": visualizations
            }
        else:
            return {
                "success": False,
                "output": clean_output,
                "error": result.stderr,
                "visualizations": visualizations  # Include any plots that were created before error
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Code execution timed out",
            "visualizations": []
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "visualizations": []
        }


def should_generate_code(state: OverallState, config: RunnableConfig) -> str:
    """Routing function to determine if code generation is needed."""
    configurable = Configuration.from_runnable_config(config)
    
    if not configurable.enable_code_interpreter:
        return "report_generator"
    
    # Check if finalize_answer determined that code analysis is needed
    code_analysis_needed = state.get("code_analysis_needed", False)
    
    if code_analysis_needed:
        print(f"🔀 Routing to code_generator: Code analysis requested by finalize_answer")
        return "code_generator"
    else:
        print(f"🔀 Routing to report_generator: No code analysis needed according to finalize_answer")
        return "report_generator"


def should_execute_code(state: OverallState, config: RunnableConfig) -> str:
    """Routing function to determine if code execution is needed."""
    
    # CRITICAL ROUTING: Only execute if we have actual Python code
    code_analysis_needed = state.get("code_analysis_needed", False)
    generated_code = state.get("generated_code", "").strip()
    
    if code_analysis_needed and generated_code and _is_actual_python_code(generated_code):
        print(f"🔀 Routing to code_executor: Python code ready for sandbox execution")
        return "code_executor"
    else:
        if not code_analysis_needed:
            print(f"🔀 Routing to report_generator: No code analysis needed")
        elif not generated_code:
            print(f"🔀 Routing to report_generator: No code was generated")
        else:
            print(f"🔀 Routing to report_generator: Generated content is not valid Python code")
        return "report_generator"


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)
builder.add_node("code_generator", code_generator)
builder.add_node("code_executor", code_executor)
builder.add_node("report_generator", report_generator)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# After finalizing answer, decide whether to generate code
builder.add_conditional_edges(
    "finalize_answer", should_generate_code, ["code_generator", "report_generator"]
)
# After code generation, decide whether to execute code
builder.add_conditional_edges(
    "code_generator", should_execute_code, ["code_executor", "report_generator"]
)
# After code execution, generate the final report
builder.add_edge("code_executor", "report_generator")
# Final report generation ends the flow
builder.add_edge("report_generator", END)

graph = builder.compile(name="azureai-deepsearch-agent")
