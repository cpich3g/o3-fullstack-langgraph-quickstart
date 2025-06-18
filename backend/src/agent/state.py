from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, Dict, Any, List

from langgraph.graph import add_messages
from typing_extensions import Annotated


import operator
from dataclasses import dataclass, field
from typing_extensions import Annotated


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str
    # New fields for enhanced research flow
    code_analysis_results: Annotated[list, operator.add]
    generated_code: str  # Python code ready for execution
    code_analysis_needed: bool  # Whether code analysis is required
    final_report: str


class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    query_list: list[Query]


class WebSearchState(TypedDict):
    search_query: str
    id: str


class CodeGeneratorState(TypedDict):
    research_content: str
    research_topic: str
    analysis_requirements: str
    code_needed: bool


class CodeExecutorState(TypedDict):
    python_code: str
    execution_context: str


class ReportGeneratorState(TypedDict):
    research_data: Dict[str, Any]
    sources: List[Dict[str, Any]]
    code_results: List[Dict[str, Any]]
    report_format: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report
