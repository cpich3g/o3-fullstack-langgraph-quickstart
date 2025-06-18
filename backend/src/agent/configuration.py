import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig



class Configuration(BaseModel):
    """The configuration for the agent."""    # Use Azure OpenAI o3 model names (deployment names or model names as configured in Azure)
    query_generator_model: str = Field(
        default="gpt-4.1-mini",
        metadata={
            "description": "The name of the Azure OpenAI o3 model to use for query generation."
        },
    )

    reflection_model: str = Field(
        default="o3",
        metadata={
            "description": "The name of the Azure OpenAI o3 model to use for reflection."
        },
    )

    answer_model: str = Field(
        default="gpt-4.1-mini",
        metadata={
            "description": "The name of the Azure OpenAI o3 model to use for answer generation."
        },
    )

    reasoning_model: str = Field(
        default="o3",
        metadata={
            "description": "The name of the Azure OpenAI o3 model to use for reasoning and reflection."
        },
    )    # Web research settings
    use_web_research: bool = Field(
        default=True,
        metadata={
            "description": "Whether to use real web research with search engines or fallback to AI-only research."
        },
    )

    search_engine: str = Field(
        default="tavily",
        metadata={
            "description": "Search engine to use for web research. Options: 'serpapi', 'tavily'."
        },
    )

    max_sources_per_query: int = Field(
        default=5,
        metadata={
            "description": "Maximum number of web sources to gather per search query."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    # Code Interpreter settings
    enable_code_interpreter: bool = Field(
        default=True,
        metadata={
            "description": "Whether to enable Azure Code Interpreter for data analysis and calculations."
        },
    )

    code_interpreter_model: str = Field(
        default="gpt-4.1-mini",
        metadata={
            "description": "The Azure OpenAI model to use for code interpretation tasks."
        },
    )

    # Azure Container Apps Dynamic Sessions settings
    pool_management_endpoint: str = Field(
        default="",
        metadata={
            "description": "Azure Container Apps dynamic sessions pool management endpoint URL."
        },
    )

    use_azure_sessions: bool = Field(
        default=True,
        metadata={
            "description": "Whether to use Azure Container Apps dynamic sessions for code execution."
        },
    )

    azure_sessions_no_auth: bool = Field(
        default=False,
        metadata={
            "description": "Set to True if the Azure Container Apps sessions endpoint is public and doesn't require authentication."
        },
    )

    # Report Generator settings
    enable_report_generator: bool = Field(
        default=True,
        metadata={
            "description": "Whether to generate a comprehensive markdown report."
        },
    )

    report_generator_model: str = Field(
        default="gpt-4.1-mini",
        metadata={
            "description": "The Azure OpenAI model to use for report generation."
        },
    )

    report_format: str = Field(
        default="markdown",
        metadata={
            "description": "The format for the final report. Options: 'markdown', 'html'."
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
