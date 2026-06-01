import os
import time
import httpx
from openai import OpenAI

AGENTS = [
    {
        "key": "data_analysis",
        "name": "Data Analysis Agent",
        "icon": "📊",
        "system": (
            "You are an expert data analyst and business intelligence specialist. "
            "Analyze the provided sales data summary and deliver clear, actionable insights. "
            "Cover: top/bottom performing products, revenue and profit trends, "
            "regional performance, customer rating patterns, and return rates. "
            "Use markdown headers (##), bullet points, and bold key numbers. "
            "Be specific — quote actual figures from the data."
        ),
    },
    {
        "key": "customer_feedback",
        "name": "Customer Feedback Agent",
        "icon": "💬",
        "system": (
            "You are a customer experience and sentiment analysis expert. "
            "Extract meaningful insights from customer reviews and ratings. "
            "Identify: dominant sentiment themes, recurring pain points, "
            "positive drivers, satisfaction patterns per product or category, "
            "and NPS-style implications. Use markdown formatting."
        ),
    },
    {
        "key": "market_opportunity",
        "name": "Market Opportunity Agent",
        "icon": "🎯",
        "system": (
            "You are a market strategy and business development expert. "
            "Based on sales performance and customer feedback, identify concrete "
            "market opportunities: under-served segments, high-growth products, "
            "cross-sell potential, regional expansion plays, and competitive gaps. "
            "Be specific and actionable. Use markdown formatting."
        ),
    },
    {
        "key": "swot",
        "name": "SWOT Analysis Agent",
        "icon": "⚡",
        "system": (
            "You are a strategic business analyst. "
            "Produce a rigorous, data-grounded SWOT analysis for this product portfolio. "
            "Every bullet must reference specific evidence from the data. "
            "Format exactly as: ## Strengths, ## Weaknesses, ## Opportunities, ## Threats "
            "— each section with 4-6 specific bullet points."
        ),
    },
    {
        "key": "feature_prioritization",
        "name": "Feature Prioritization Agent",
        "icon": "🔢",
        "system": (
            "You are a senior product manager specializing in prioritization frameworks. "
            "Based on all analysis, recommend specific product improvements and new features. "
            "Use a MoSCoW breakdown (Must-Have / Should-Have / Nice-to-Have) plus a "
            "top-3 Quick Wins list. Ground every recommendation in the data. Use markdown."
        ),
    },
    {
        "key": "opportunity_scoring",
        "name": "Opportunity Scoring Agent",
        "icon": "🏆",
        "system": (
            "You are a product strategy expert specializing in opportunity matrices. "
            "Score each product on these 4 dimensions (1-10 each), then compute an Overall Score:\n"
            "- Market Opportunity: growth potential and market size\n"
            "- Financial Attractiveness: profit margin and ROI\n"
            "- Customer Demand: based on ratings, sales volume, and feedback\n"
            "- Competitive Position: relative advantage implied by data\n\n"
            "Present results in a markdown table with columns: "
            "Product | Market Opp. | Financial | Customer Demand | Competitive | **Overall Score** | Recommendation.\n"
            "Recommendation must be one of: Invest / Maintain / Optimise / Divest.\n"
            "Then write a brief narrative (3-4 bullets) on the top 3 opportunities."
        ),
    },
    {
        "key": "roadmap",
        "name": "Roadmap Generation Agent",
        "icon": "🗺️",
        "system": (
            "You are an expert product roadmap planner. "
            "Create a realistic, data-driven 4-quarter product roadmap. "
            "For each quarter use this exact format:\n\n"
            "## Q[N] [Year]: [Theme]\n"
            "**Focus**: one-line strategic focus\n"
            "**Key Initiatives**:\n- initiative 1\n- initiative 2\n- initiative 3\n"
            "**Success Metrics**: 2-3 KPIs\n"
            "**Dependencies**: key blockers or prerequisites\n\n"
            "Ground every initiative in the feature priorities, opportunity scores, "
            "customer feedback, and SWOT analysis provided."
        ),
    },
    {
        "key": "executive_summary",
        "name": "Executive Report Agent",
        "icon": "📋",
        "system": (
            "You are a senior strategy consultant writing for C-suite leadership. "
            "Synthesize all prior analysis into a crisp executive report. "
            "Structure: ## Executive Summary (3 sentences) → "
            "## Key Findings (top 5 bullets) → "
            "## Strategic Recommendations (top 5 bullets) → "
            "## 30-60-90 Day Action Plan → "
            "## Success Metrics. "
            "Be decisive, specific, and business-focused."
        ),
    },
]


def _build_prompt(agent: dict, summary: dict, prev: dict) -> str:
    key = agent["key"]
    base = summary["text"]

    if key == "data_analysis":
        return f"Analyze this sales data and provide detailed insights:\n\n{base}"

    if key == "customer_feedback":
        return (
            f"Analyze customer feedback from this sales data:\n\n{base}\n\n"
            f"Data Analysis Context:\n{prev.get('data_analysis', '')[:1200]}"
        )

    if key == "market_opportunity":
        return (
            f"Identify market opportunities:\n\n{base[:2000]}\n\n"
            f"Data Analysis:\n{prev.get('data_analysis', '')[:800]}\n\n"
            f"Customer Insights:\n{prev.get('customer_feedback', '')[:600]}"
        )

    if key == "swot":
        return (
            f"Create a SWOT analysis:\n\n{base[:1800]}\n\n"
            f"Data Analysis:\n{prev.get('data_analysis', '')[:600]}\n\n"
            f"Customer Insights:\n{prev.get('customer_feedback', '')[:500]}\n\n"
            f"Market Opportunities:\n{prev.get('market_opportunity', '')[:500]}"
        )

    if key == "feature_prioritization":
        return (
            f"Recommend feature priorities:\n\n{base[:1500]}\n\n"
            f"Customer Feedback:\n{prev.get('customer_feedback', '')[:700]}\n\n"
            f"SWOT:\n{prev.get('swot', '')[:600]}"
        )

    if key == "opportunity_scoring":
        return (
            f"Score each product for opportunity:\n\n{base[:1500]}\n\n"
            f"Data Analysis:\n{prev.get('data_analysis', '')[:600]}\n\n"
            f"Customer Feedback:\n{prev.get('customer_feedback', '')[:500]}\n\n"
            f"Market Opportunities:\n{prev.get('market_opportunity', '')[:500]}\n\n"
            f"Feature Priorities:\n{prev.get('feature_prioritization', '')[:400]}"
        )

    if key == "roadmap":
        return (
            f"Build a quarterly product roadmap:\n\n{base[:1200]}\n\n"
            f"Opportunity Scores:\n{prev.get('opportunity_scoring', '')[:700]}\n\n"
            f"Feature Priorities:\n{prev.get('feature_prioritization', '')[:700]}\n\n"
            f"SWOT:\n{prev.get('swot', '')[:500]}"
        )

    # executive_summary
    return (
        f"Synthesize all analysis into an executive report.\n\n"
        f"Sales Overview:\n{base[:800]}\n\n"
        f"Data Analysis:\n{prev.get('data_analysis', '')[:400]}\n\n"
        f"Customer Insights:\n{prev.get('customer_feedback', '')[:400]}\n\n"
        f"Market Opportunities:\n{prev.get('market_opportunity', '')[:400]}\n\n"
        f"SWOT:\n{prev.get('swot', '')[:400]}\n\n"
        f"Feature Priorities:\n{prev.get('feature_prioritization', '')[:400]}\n\n"
        f"Opportunity Scores:\n{prev.get('opportunity_scoring', '')[:400]}\n\n"
        f"Roadmap:\n{prev.get('roadmap', '')[:400]}"
    )


def run_all_agents(api_key: str, summary: dict, progress_callback=None):
    """
    Returns (results, metadata).
    results  : {agent_key: str}
    metadata : {agent_key: {name, icon, time_s, prompt_tokens, completion_tokens, total_tokens}}
    """
    base_url = os.getenv("OPENAI_BASE_URL")
    http_client = httpx.Client(verify=False)  # gateway uses a private CA
    client = (
        OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        if base_url else
        OpenAI(api_key=api_key)
    )
    results: dict = {}
    metadata: dict = {}

    for i, agent in enumerate(AGENTS):
        if progress_callback:
            progress_callback(i, agent["name"])

        prompt = _build_prompt(agent, summary, results)
        t0 = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": agent["system"]},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        elapsed = round(time.time() - t0, 2)

        results[agent["key"]] = response.choices[0].message.content
        metadata[agent["key"]] = {
            "name":               agent["name"],
            "icon":               agent["icon"],
            "time_s":             elapsed,
            "prompt_tokens":      response.usage.prompt_tokens,
            "completion_tokens":  response.usage.completion_tokens,
            "total_tokens":       response.usage.total_tokens,
        }

    return results, metadata


def chat_with_assistant(
    api_key: str,
    question: str,
    summary: dict,
    agent_results: dict,
    history: list,
) -> str:
    base_url = os.getenv("OPENAI_BASE_URL")
    http_client = httpx.Client(verify=False)  # gateway uses a private CA
    client = (
        OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        if base_url else
        OpenAI(api_key=api_key)
    )

    system = (
        "You are an AI Product Strategy Assistant with complete analysis context. "
        "Answer questions concisely and cite specific data points wherever possible.\n\n"
        f"Sales Overview:\n{summary['text'][:1000]}\n\n"
        f"Data Analysis:\n{agent_results.get('data_analysis', '')[:350]}\n\n"
        f"Customer Insights:\n{agent_results.get('customer_feedback', '')[:350]}\n\n"
        f"Market Opportunities:\n{agent_results.get('market_opportunity', '')[:350]}\n\n"
        f"SWOT:\n{agent_results.get('swot', '')[:350]}\n\n"
        f"Feature Priorities:\n{agent_results.get('feature_prioritization', '')[:300]}\n\n"
        f"Opportunity Scores:\n{agent_results.get('opportunity_scoring', '')[:300]}\n\n"
        f"Roadmap:\n{agent_results.get('roadmap', '')[:300]}\n\n"
        f"Executive Summary:\n{agent_results.get('executive_summary', '')[:350]}"
    )

    messages = [{"role": "system", "content": system}]
    for msg in history[-8:]:
        messages.append(msg)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content
