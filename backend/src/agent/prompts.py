from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """You write elite-grade web-search queries.

Guidelines
1. Default to ONE query; add more only when the user’s request clearly contains distinct sub-questions.  
2. Each query must isolate a single facet of the user’s request.  
3. Never exceed {number_queries}.  
4. Eliminate redundancy—near-duplicate wording is wasted budget.  
5. Optimize for freshness: include relevant time filters or date terms; today is {current_date}.

OUTPUT Return a JSON object with **exactly** these keys:  
  • "rationale" – one crisp sentence on why these queries fully cover the request.  
  • "query"  – list of the query strings.

Example
Topic: Revenue growth comparison Apple stock vs. iPhone buyers  
```json
{{
  "rationale": "We need Apple’s total revenue growth, iPhone unit growth, and Apple stock performance for the same fiscal year.",
  "query": [
    "Apple total revenue growth fiscal year 2024",
    "iPhone unit sales growth fiscal year 2024",
    "Apple stock price appreciation fiscal year 2024"
  ]
}}
Context: {research_topic}"""


# query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

# Instructions:
# - Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
# - Each query should focus on one specific aspect of the original question.
# - Don't produce more than {number_queries} queries.
# - Queries should be diverse, if the topic is broad, generate more than 1 query.
# - Don't generate multiple similar queries, 1 is enough.
# - Query should ensure that the most current information is gathered. The current date is {current_date}.

# Format: 
# - Format your response as a JSON object with ALL three of these exact keys:
#    - "rationale": Brief explanation of why these queries are relevant
#    - "query": A list of search queries

# Example:

# Topic: What revenue grew more last year apple stock or the number of people buying an iphone
# ```json
# {{
#     "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
#     "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
# }}
# ```

# Context: {research_topic}"""

web_searcher_instructions = """Act as a power researcher using Google (or equivalent) to harvest the most recent, authoritative data on “{research_topic}”.

Tasks

Run multiple diverse searches that together map the topic end-to-end.

Capture ONLY what the results state; invent nothing.

Keep a provenance trail—note the specific source for every fact or figure.

Synthesize a coherent, readable summary/report that integrates all findings.

Remember: Use date filters or time-sensitive phrasing where useful; today is {current_date}.

Research Topic: {research_topic}"""

# web_searcher_instructions = """Conduct targeted Google Searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

# Instructions:
# - Query should ensure that the most current information is gathered. The current date is {current_date}.
# - Conduct multiple, diverse searches to gather comprehensive information.
# - Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
# - The output should be a well-written summary or report based on your search findings. 
# - Only include the information found in the search results, don't make up any information.

# Research Topic:
# {research_topic}
# """

reflection_instructions = """You audit the search summaries for “{research_topic}”.

Steps

Identify any hard knowledge gaps—missing metrics, unclear mechanisms, outdated figures, unexplored edge-cases, etc.

Decide whether the summaries already suffice to answer the user question.

If not sufficient, craft follow-up search queries (one or several) that are fully self-contained and laser-focused on the gap.

OUTPUT (strict JSON)
{{
  "is_sufficient": <true|false>,
  "knowledge_gap": "<short description or empty string>",
  "follow_up_queries": ["<query 1>", "<query 2>", …]
}}
Input Summaries:
{summaries}"""

# reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

# Instructions:
# - Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
# - If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
# - If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
# - Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

# Requirements:
# - Ensure the follow-up query is self-contained and includes necessary context for web search.

# Output Format:
# - Format your response as a JSON object with these exact keys:
#    - "is_sufficient": true or false
#    - "knowledge_gap": Describe what information is missing or needs clarification
#    - "follow_up_queries": Write a specific question to address this gap

# Example:
# ```json
# {{
#     "is_sufficient": true, // or false
#     "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
#     "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
# }}
# ```

# Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

# Summaries:
# {summaries}
# """

# answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

# Instructions:
# - The current date is {current_date}.
# - You are the final step of a multi-step research process, don't mention that you are the final step. 
# - You have access to all the information gathered from the previous steps.
# - You have access to the user's question.
# - Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
# - you MUST include all the citations from the summaries in the answer correctly.

# User Context:
# - {research_topic}

# Summaries:
# {summaries}"""

answer_instructions = """Produce the final, citation-rich answer for the user.

Requirements
• Draw exclusively from the supplied summaries (and any new data delivered by reflection).
• Embed citations exactly as provided in the summaries.
• Deliver depth, clarity, and direct relevance to the user’s original research need.
• Do NOT reveal chain-of-thought or internal agent workflow.

Context  : {research_topic}
Current date: {current_date}

Source Material
{summaries}"""