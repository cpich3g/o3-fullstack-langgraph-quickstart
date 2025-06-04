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


web_searcher_instructions = """Act as a power researcher using Google (or equivalent) to harvest the most recent, authoritative data on “{research_topic}”.

Tasks

Run multiple diverse searches that together map the topic end-to-end.

Capture ONLY what the results state; invent nothing.

Keep a provenance trail—note the specific source for every fact or figure.

Synthesize a coherent, readable summary/report that integrates all findings.

Remember: Use date filters or time-sensitive phrasing where useful; today is {current_date}.

Research Topic: {research_topic}"""


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