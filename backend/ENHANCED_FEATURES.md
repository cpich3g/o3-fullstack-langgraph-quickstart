# Enhanced LangGraph Agent with Azure Code Interpreter and Report Generator

This enhanced version of the LangGraph deep research agent includes two powerful new nodes:

## 🧮 Azure Code Interpreter
Performs automated data analysis, calculations, and visualizations using **Azure Container Apps dynamic sessions** for secure, scalable code execution.

### Architecture:
- **Primary**: Azure Container Apps dynamic sessions (Hyper-V isolated sandboxes)
- **Fallback**: Local subprocess execution with safety checks
- **Security**: Hyper-V isolation, secure credential management
- **Scalability**: Automatic scaling with Azure Container Apps

### Features:
- **Secure Code Execution**: Runs in Hyper-V isolated Azure Container Apps sessions
- **Automated Code Generation**: Generates Python code for data analysis based on research findings
- **Rich Environment**: Pre-installed packages (NumPy, pandas, scikit-learn, matplotlib, seaborn)
- **Data Visualization**: Creates charts and graphs with automatic image handling
- **Statistical Analysis**: Performs calculations and statistical analysis on research data
- **Error Handling**: Robust error handling and validation
- **File Upload Support**: Can upload data files to sessions for analysis

### Capabilities:
- Extract numerical data from research results
- Perform calculations and statistical analysis
- Generate visualizations (matplotlib, seaborn) with base64 image support
- Process data with pandas and numpy
- Upload and analyze data files
- Provide insights based on computational analysis
- Automatic fallback to local execution if Azure sessions unavailable

## 📊 Report Generator Agent
Creates comprehensive, well-structured markdown reports synthesizing all research findings.

### Features:
- **Professional Formatting**: Generates clean markdown reports with proper structure
- **Source Integration**: Seamlessly integrates citations and references
- **Code Analysis Integration**: Incorporates code analysis results into the report
- **Executive Summary**: Provides high-level overview and key findings
- **Methodology Section**: Documents the research process and approach

### Report Structure:
1. **Executive Summary** - High-level overview and key findings
2. **Research Methodology** - Documentation of research approach
3. **Key Findings** - Main research results and insights
4. **Data Analysis & Calculations** - Code analysis results and visualizations
5. **Sources & References** - Properly formatted citations
6. **Conclusions & Recommendations** - Actionable insights and next steps

## 🔧 Configuration Options

The enhanced agent includes new configuration parameters:

### Code Interpreter Settings:
```python
enable_code_interpreter: bool = True  # Enable/disable code interpreter
code_interpreter_model: str = "gpt-4.1-mini"  # Azure OpenAI model for code tasks
use_azure_sessions: bool = True  # Use Azure Container Apps dynamic sessions
pool_management_endpoint: str = ""  # Azure Container Apps sessions endpoint
```

### Report Generator Settings:
```python
enable_report_generator: bool = True  # Enable/disable report generation
report_generator_model: str = "gpt-4.1-mini"  # Azure OpenAI model for reports
report_format: str = "markdown"  # Report format (markdown/html)
```

## 🚀 Updated Research Flow

The enhanced research flow now includes intelligent routing:

1. **Query Generation** → Generate search queries
2. **Web Research** → Parallel web research execution
3. **Reflection** → Evaluate research completeness
4. **Finalize Answer** → Synthesize initial findings
5. **Smart Routing** → Determine if code analysis is beneficial
6. **Code Interpreter** (conditional) → Perform data analysis
7. **Report Generator** → Generate comprehensive report

## 🔀 Intelligent Routing

The agent intelligently determines when to use the code interpreter based on:
- Presence of numerical data in research results
- Keywords indicating quantitative analysis needs
- Research topics requiring calculations or visualizations

Keywords that trigger code interpretation:
- data, statistics, numbers, percentage
- growth, trend, comparison, analysis
- calculate, chart, graph, revenue
- profit, sales, market share, financial, metrics

## 🛡️ Safety Features

### Azure Container Apps Dynamic Sessions (Primary):
- **Hyper-V Isolation**: Complete isolation using Hyper-V containers
- **Secure Authentication**: Uses DefaultAzureCredential for secure access
- **Automatic Scaling**: Scales based on demand
- **Pre-configured Environment**: Safe, curated Python environment
- **Image Support**: Automatic handling of matplotlib/seaborn visualizations
- **Timeout Protection**: Built-in execution timeouts
- **Resource Limits**: Controlled execution environment

### Subprocess Fallback (Secondary):
- **Sandboxed Environment**: Code runs in isolated temporary files
- **Keyword Filtering**: Blocks dangerous operations (file I/O, system calls)
- **Timeout Protection**: 30-second execution timeout
- **Error Handling**: Graceful handling of execution failures
- **Resource Limits**: Controlled execution environment

### Available Libraries (Both Methods):
- pandas, numpy (data manipulation)
- matplotlib, seaborn (visualization)
- scikit-learn (machine learning)
- datetime, json (utilities)
- Basic mathematical operations

### Blocked Operations (Subprocess Only):
- File system access (open, file, remove)
- System operations (os, subprocess, sys)
- Network operations
- Code evaluation (exec, eval)

## 📦 Dependencies

New packages added for enhanced functionality:

```toml
"langchain-azure-dynamic-sessions",  # Azure Container Apps dynamic sessions
"langchain-community",               # LangChain community tools
"pandas>=2.0.0",                    # Data manipulation and analysis
"numpy>=1.24.0",                    # Numerical computing
"matplotlib>=3.7.0",                # Plotting and visualization
"seaborn>=0.12.0",                  # Statistical data visualization
```

## 🔧 Setup Instructions

### 1. Azure Container Apps Dynamic Sessions Setup

Follow the [Azure Container Apps sessions documentation](https://docs.microsoft.com/en-us/azure/container-apps/sessions) to:

1. Create a session pool in Azure Container Apps
2. Get the pool management endpoint URL
3. Configure authentication (Azure CLI login or service principal)

### 2. Environment Configuration

```bash
# Set required environment variables
export AZURE_OPENAI_API_KEY="your_key_here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Set Azure Container Apps sessions endpoint
export AZURE_POOL_MANAGEMENT_ENDPOINT="your_sessions_endpoint_here"

# For public endpoints that don't require authentication
export AZURE_SESSIONS_NO_AUTH="true"

# Authenticate with Azure (only if required by your endpoint)
az login  # Azure CLI authentication
# OR configure service principal environment variables
```

### 3. Package Installation

```bash
pip install langchain-azure-dynamic-sessions langchain-community pandas numpy matplotlib seaborn
```

### 4. Testing

```bash
# Test Azure Container Apps sessions connection
python test_azure_sessions.py

# Test the full enhanced agent
python test_enhanced_agent.py
```

## 🧪 Testing

Use the provided test script to validate the enhanced functionality:

```bash
python test_enhanced_agent.py
```

The test script validates:
- Configuration system
- Code interpreter functionality
- Report generation
- End-to-end research flow

## 📝 Example Usage

```python
from agent.graph import graph
from langchain_core.messages import HumanMessage

# Configure the agent
config = {
    "configurable": {
        "enable_code_interpreter": True,
        "enable_report_generator": True,
        "use_web_research": True,
        "max_research_loops": 2,
        "number_of_initial_queries": 3
    }
}

# Research query requiring data analysis
message = HumanMessage(content="""
Analyze Tesla's financial performance in 2024. 
Include revenue growth, stock performance analysis, 
and market share calculations with visualizations.
""")

# Execute the research
result = await graph.ainvoke(
    {"messages": [message]},
    config=config
)

# Access the comprehensive report
final_report = result["final_report"]
code_analysis = result["code_analysis_results"]
sources = result["sources_gathered"]
```

## 🔍 Output Structure

The enhanced agent returns:

```python
{
    "messages": [AIMessage(...)],  # Final message with report
    "final_report": str,           # Comprehensive markdown report
    "code_analysis_results": [     # Code analysis results
        {
            "code_executed": str,          # Python code that was executed
            "results": str,                # Analysis results and findings
            "visualizations": [            # Generated charts/graphs
                {
                    "type": "image",
                    "format": "png",
                    "base64_data": str,
                    "description": str
                }
            ],
            "insights": str,               # Key insights from analysis
            "errors": str,                 # Any errors encountered
            "execution_method": str,       # "azure_sessions" or "subprocess_fallback"
            "execution_time_ms": int,      # Execution time (Azure sessions only)
            "status": str,                 # Execution status
            "stdout": str,                 # Standard output
            "stderr": str                  # Standard error
        }
    ],
    "sources_gathered": list,      # Research sources
    "web_research_result": list,   # Raw research results
    "search_query": list           # Search queries used
}
```

## 🎯 Best Practices

1. **Enable Both Features**: Use both code interpreter and report generator for comprehensive analysis
2. **Appropriate Queries**: Frame research questions to include quantitative aspects
3. **Review Configuration**: Adjust models and settings based on complexity needs
4. **Monitor Resources**: Code execution has timeouts and safety limits
5. **Validate Results**: Always review generated code and calculations

## 🚨 Limitations

- Code execution limited to safe, predefined libraries
- 30-second timeout for code execution
- No file system or network access during code execution
- Visualization output may be limited in some environments
- Report quality depends on research data availability

## 🔧 Troubleshooting

### Common Issues:

1. **Azure Sessions Authentication Failed** (Most Common):
   ```
   DefaultAzureCredential failed to retrieve a token...
   ```
   **Solutions:**
   - **For Public Endpoints**: Set `AZURE_SESSIONS_NO_AUTH=true` in your `.env` file
   - **For Authenticated Endpoints**: Run `az login` or configure service principal
   - **Test Connection**: Run `python test_azure_sessions.py` to diagnose the issue
   - **Verify Endpoint**: Ensure your endpoint URL is correct and accessible

2. **Azure Sessions Not Available**: 
   - Check if `AZURE_POOL_MANAGEMENT_ENDPOINT` is set correctly
   - Verify network connectivity to the endpoint
   - Ensure session pool is created and accessible
   - **Automatic Fallback**: System will use subprocess execution automatically

3. **Authentication Method Priority**:
   ```
   1. Environment Variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
   2. Managed Identity (when running in Azure)
   3. Azure CLI (az login)
   4. VS Code Azure Extension
   5. Azure PowerShell
   6. Azure Developer CLI
   ```

4. **Public vs Authenticated Endpoints**:
   - **Public**: No authentication required, set `AZURE_SESSIONS_NO_AUTH=true`
   - **Private**: Requires Azure authentication, ensure proper credentials

5. **Code Execution Fails**: 
   - Check if code contains restricted operations (subprocess only)
   - Verify network connectivity to Azure (sessions)
   - Check Azure Container Apps quotas and limits

6. **No Code Analysis**: 
   - Ensure research contains numerical/quantitative data
   - Check if analysis keywords are present in research content

7. **Report Generation Errors**: 
   - Verify Azure OpenAI model availability
   - Check API quotas and rate limits

8. **Missing Dependencies**: 
   - Install required packages: `pip install langchain-azure-dynamic-sessions`
   - Verify package versions compatibility

### Debug Configuration:

Set environment variables for enhanced debugging:
```bash
export AZURE_OPENAI_DEBUG=true
export LANGGRAPH_DEBUG=true
export AZURE_SESSIONS_DEBUG=true
```

### Azure Container Apps Sessions Troubleshooting:

```bash
# Test Azure authentication
az account show

# List available session pools (if you have access)
az containerapp sessionpool list

# Check Azure Container Apps extension
az extension add --name containerapp
az extension update --name containerapp
```

## Enhanced Code Generation and Execution Separation

### Critical Principle: Sandbox Receives Only Python Code

The enhanced agent implements strict separation between code generation and execution with multiple validation layers:

#### Code Generation Phase
- **Smart Decision Making**: LLM analyzes research content to determine if computational analysis adds value
- **Conservative Approach**: Most research queries don't need code - only mathematical, statistical, or visualization tasks
- **Structured Validation**: Generated content must pass Python syntax and content validation

#### Execution Phase  
- **Python-Only Rule**: Only validated Python code reaches the execution sandbox
- **Multiple Gates**: Code validation happens at generation, routing, and execution phases
- **Safe Fallback**: If no valid code exists but analysis was requested, the system gracefully continues without execution

#### Key Validation Function
```python
def _is_actual_python_code(code_content: str) -> bool:
    # Validates that content is executable Python code
    # Checks for Python syntax indicators
    # Compiles code to verify syntax
    # Rejects text explanations, comments-only, or non-code content
```

#### Routing Logic
```python
def should_execute_code(state: OverallState, config: RunnableConfig) -> str:
    # Routes to execution ONLY if:
    # 1. Code analysis was marked as needed
    # 2. Actual Python code was generated  
    # 3. Code passes validation checks
    # Otherwise routes directly to report generation
```

#### Benefits
- **Security**: Only validated code reaches sandbox environment
- **Efficiency**: Computational resources used only when truly beneficial  
- **Reliability**: Multiple validation layers prevent execution errors
- **Transparency**: Clear logging of all decision points and validations

See `CODE_SEPARATION_ARCHITECTURE.md` for detailed technical documentation.
