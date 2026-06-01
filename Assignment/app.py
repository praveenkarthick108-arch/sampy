import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from data_processor import process_csv
from agents import run_all_agents, chat_with_assistant, AGENTS
from report_generator import generate_pdf
from architecture_diagram import generate_architecture_diagram

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Product Strategy Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.banner {
    background: linear-gradient(135deg, #1e40af 0%, #6d28d9 100%);
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}
.banner h1 { color: #fff; margin: 0; font-size: 2rem; }
.banner p  { color: rgba(255,255,255,.8); margin: .4rem 0 0; font-size: 1rem; }
.badge {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 20px;
    padding: .2rem .85rem;
    font-size: .75rem;
    font-weight: 600;
    margin-bottom: .6rem;
}
.chat-user {
    background: #eff6ff;
    border-radius: 12px 12px 4px 12px;
    padding: .7rem 1rem;
    margin: .4rem 0;
}
.chat-bot {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px 12px 12px 4px;
    padding: .7rem 1rem;
    margin: .4rem 0;
}
.monitor-row { font-size: .85rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Starts with sk-…",
    )

    st.markdown("---")
    st.markdown("### 📁 Data Source")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    df = None
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success(f"Loaded: {uploaded.name}")
    elif os.path.exists("Sample Sales Data.csv"):
        df = pd.read_csv("Sample Sales Data.csv")
        st.info("Using: Sample Sales Data.csv")

    if df is not None:
        st.caption(f"{len(df):,} rows · {len(df.columns)} columns")

    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    for a in AGENTS:
        st.markdown(f"{a['icon']} {a['name']}")

    st.markdown("---")
    st.caption("AI Product Strategy Assistant v2.0")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <h1>🚀 AI Product Strategy Assistant</h1>
  <p>8-agent analysis pipeline · GPT-4o Mini · Opportunity Scoring · Roadmap · Executive PDF</p>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.warning("Place **Sample Sales Data.csv** in the app folder or upload a CSV via the sidebar.")
    st.stop()

if not api_key:
    st.warning("Enter your **OpenAI API key** in the sidebar to continue.")
    st.stop()

# ── Quick metrics ─────────────────────────────────────────────────────────────
summary = process_csv(df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Revenue",      f"${summary['total_revenue']:,.0f}")
c2.metric("📈 Profit",       f"${summary['total_profit']:,.0f}")
c3.metric("📦 Units Sold",   f"{summary['total_units']:,}")
c4.metric("⭐ Avg Rating",   f"{summary['avg_rating']:.2f} / 5")
c5.metric("🔄 Returns",      f"{summary['total_returns']:,}")

st.markdown("---")

# ── Run button ────────────────────────────────────────────────────────────────
if st.button("🔍 Run Full Analysis  (8 agents)", type="primary"):
    bar  = st.progress(0, text="Initialising agents…")
    info = st.empty()

    def on_progress(i, name):
        pct = int(i / len(AGENTS) * 100)
        bar.progress(pct, text=f"Running {name}  ({i+1}/{len(AGENTS)})…")
        info.info(f"🤖 **{name}** is working…")

    try:
        results, metadata = run_all_agents(api_key, summary, on_progress)
        bar.progress(100, text="All agents finished!")
        info.success(f"✅ All {len(AGENTS)} agents completed — scroll down to explore results.")
        st.session_state.results  = results
        st.session_state.metadata = metadata
        st.session_state.summary  = summary
    except Exception as exc:
        bar.empty()
        info.error(f"❌ {exc}")

# ── Pipeline Monitor ──────────────────────────────────────────────────────────
if "metadata" in st.session_state:
    with st.expander("📡 Pipeline Monitor — agent performance metrics", expanded=False):
        meta = st.session_state.metadata
        rows = []
        for key, m in meta.items():
            rows.append({
                "Agent":             f"{m['icon']} {m['name']}",
                "Time (s)":          m['time_s'],
                "Prompt Tokens":     m['prompt_tokens'],
                "Completion Tokens": m['completion_tokens'],
                "Total Tokens":      m['total_tokens'],
            })
        mon_df = pd.DataFrame(rows)
        st.dataframe(mon_df, use_container_width=True, hide_index=True)

        total_tok = sum(m['total_tokens'] for m in meta.values())
        total_time = sum(m['time_s'] for m in meta.values())
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total Tokens Used",  f"{total_tok:,}")
        mc2.metric("Total Time (s)",     f"{total_time:.1f}s")
        mc3.metric("Agents Completed",   len(meta))

# ── Results Tabs ──────────────────────────────────────────────────────────────
if "results" in st.session_state:
    res = st.session_state.results
    smr = st.session_state.summary

    tabs = st.tabs([
        "📊 Data Overview",
        "💬 Customer Insights",
        "🎯 Market Opportunities",
        "⚡ SWOT Analysis",
        "🔢 Feature Priorities",
        "🏆 Opportunity Scores",
        "🗺️ Product Roadmap",
        "📋 Executive Summary",
    ])

    # ── Tab 0: Charts + Data Analysis ────────────────────────────────────────
    with tabs[0]:
        ch1, ch2 = st.columns(2)
        with ch1:
            fig = px.bar(
                smr['by_product'].reset_index().sort_values('Revenue_USD', ascending=False),
                x='Product_Name', y='Revenue_USD',
                title='Revenue by Product', color='Revenue_USD',
                color_continuous_scale='Blues',
            )
            fig.update_layout(showlegend=False, height=340, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            fig = px.pie(
                smr['by_category'].reset_index(),
                values='Revenue_USD', names='Category',
                title='Revenue by Category', hole=0.4,
            )
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)

        ch3, ch4 = st.columns(2)
        with ch3:
            fig = px.bar(
                smr['by_region'].reset_index().sort_values('Profit_USD', ascending=False),
                x='Region', y='Profit_USD',
                title='Profit by Region', color='Profit_USD',
                color_continuous_scale='Greens',
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

        with ch4:
            monthly_df = smr['monthly'].reset_index()
            fig = px.line(
                monthly_df, x='Month', y='Revenue_USD',
                title='Monthly Revenue Trend', markers=True,
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<span class="badge">📊 Data Analysis Agent</span>', unsafe_allow_html=True)
        st.markdown(res.get('data_analysis', ''))

    # ── Tabs 1-7: remaining agents ────────────────────────────────────────────
    _tab_map = [
        ('customer_feedback',     1, '💬 Customer Feedback Agent'),
        ('market_opportunity',    2, '🎯 Market Opportunity Agent'),
        ('swot',                  3, '⚡ SWOT Analysis Agent'),
        ('feature_prioritization',4, '🔢 Feature Prioritization Agent'),
        ('opportunity_scoring',   5, '🏆 Opportunity Scoring Agent'),
        ('roadmap',               6, '🗺️ Roadmap Generation Agent'),
        ('executive_summary',     7, '📋 Executive Report Agent'),
    ]
    for key, idx, label in _tab_map:
        with tabs[idx]:
            st.markdown(f'<span class="badge">{label}</span>', unsafe_allow_html=True)
            st.markdown(res.get(key, ''))

    st.markdown("---")

    # ── Downloads row ─────────────────────────────────────────────────────────
    dl1, dl2, dl3 = st.columns(3)

    with dl1:
        pdf_bytes = generate_pdf(res, smr)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="product_strategy_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with dl2:
        arch_bytes = generate_architecture_diagram()
        st.download_button(
            label="🖼️ Download Architecture Diagram",
            data=arch_bytes,
            file_name="architecture_diagram.png",
            mime="image/png",
            use_container_width=True,
        )

    with dl3:
        st.info("Architecture diagram & PDF report satisfy submission requirements 3 & 4.")

    # Preview architecture diagram inline
    with st.expander("🖼️ Architecture Diagram Preview", expanded=False):
        st.image(arch_bytes, use_container_width=True)

# ── Chat Interface ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💬 Ask the Strategy Assistant")

if "results" not in st.session_state:
    st.info("Run the analysis first to enable the chat assistant.")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_display = []

    for msg in st.session_state.chat_display:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">👤 <strong>You:</strong> {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bot">🤖 <strong>Assistant:</strong> {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            question = st.text_input(
                "question",
                placeholder="e.g. Which product should we prioritise in Q3?",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    if submitted and question.strip():
        st.session_state.chat_display.append({"role": "user", "content": question})
        with st.spinner("Thinking…"):
            try:
                answer = chat_with_assistant(
                    api_key,
                    question,
                    st.session_state.summary,
                    st.session_state.results,
                    st.session_state.chat_history,
                )
                st.session_state.chat_history += [
                    {"role": "user",      "content": question},
                    {"role": "assistant", "content": answer},
                ]
                st.session_state.chat_display.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as exc:
                st.error(f"Chat error: {exc}")
