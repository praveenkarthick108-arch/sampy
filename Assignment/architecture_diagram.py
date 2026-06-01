import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── palette ───────────────────────────────────────────────────────────────────
BG  = '#F8FAFC'
DK  = '#0F172A'
GY  = '#64748B'
BL  = '#1E40AF'
BL2 = '#3B82F6'
BL3 = '#DBEAFE'
PU  = '#6D28D9'
PU2 = '#8B5CF6'
GR  = '#065F46'
GR2 = '#D1FAE5'
AG  = '#EEF2FF'
WH  = '#FFFFFF'
SH  = '#CBD5E1'


def _box(ax, cx, cy, w, h, bg, text, fg=WH, fs=8.5, border=None):
    ax.add_patch(FancyBboxPatch(
        (cx - w/2 + 0.04, cy - h/2 - 0.04), w, h,
        boxstyle='round,pad=0.07', facecolor=SH,
        edgecolor='none', linewidth=0, zorder=2, alpha=0.4))
    ax.add_patch(FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle='round,pad=0.07', facecolor=bg,
        edgecolor=border or bg, linewidth=1.4, zorder=3))
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fs, color=fg, fontweight='bold',
            zorder=10, multialignment='center', linespacing=1.4)


def _band(ax, x0, y0, w, h, fill, edge):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle='round,pad=0.06', facecolor=fill,
        edgecolor=edge, linewidth=1.2, zorder=1))


def _label(ax, x, y, text, color):
    ax.text(x, y, text, ha='left', va='center',
            fontsize=7.5, color=color, fontweight='bold',
            zorder=10, alpha=0.85)


def _arr(ax, x0, y0, x1, y1, col=GY, lw=1.8, rad=0.0):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle='->', color=col, lw=lw,
                    connectionstyle=f'arc3,rad={rad}'),
                zorder=5)


def generate_architecture_diagram() -> bytes:
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0.5, 10)
    ax.axis('off')
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # ── title ─────────────────────────────────────────────────────────────────
    ax.text(8, 9.60, 'AI Product Strategy Assistant',
            ha='center', va='center',
            fontsize=18, fontweight='bold', color=DK, zorder=10)
    ax.text(8, 9.22, 'System Architecture  ·  8-Agent Pipeline  ·  GPT-4o Mini',
            ha='center', va='center',
            fontsize=10, color=GY, zorder=10)

    # ── INPUT LAYER ───────────────────────────────────────────────────────────
    _label(ax, 0.75, 8.82, 'INPUT LAYER', BL2)
    _band(ax, 0.65, 7.95, 14.7, 0.82, BL3, BL2)
    _box(ax,  4.4, 8.36, 4.8, 0.60, BL2,
         'Sales Data CSV\n(Date  ·  Product  ·  Revenue  ·  Reviews)', WH, 8.5, BL)
    _box(ax, 11.6, 8.36, 4.8, 0.60, BL2,
         'Uploaded Documents\n(Research  ·  Competitor  ·  Surveys)', WH, 8.5, BL)

    _arr(ax, 8, 7.95, 8, 7.62, BL, 2.0)

    # ── DATA PROCESSOR ────────────────────────────────────────────────────────
    _box(ax, 8, 7.31, 6.0, 0.58, BL,
         'Data Processor   (Pandas)\nStatistics  ·  Summaries  ·  Context Builder',
         WH, 9.5, BL)

    _arr(ax, 8, 7.02, 8, 6.72, BL, 2.0)

    # ── AGENT PIPELINE ────────────────────────────────────────────────────────
    _label(ax, 0.75, 6.62, 'AGENT PIPELINE  (GPT-4o Mini  ·  8 Agents)', PU2)
    _band(ax, 0.65, 4.22, 14.7, 2.32, AG, '#C7D2FE')

    # row 1: agents 1–4
    R1 = 5.98
    r1 = [(2.2,  '1.  Data\nAnalysis'),
          (5.5,  '2.  Customer\nFeedback'),
          (8.8,  '3.  Market\nOpportunity'),
          (12.1, '4.  SWOT\nAnalysis')]
    for i, (cx, lbl) in enumerate(r1):
        _box(ax, cx, R1, 2.7, 0.78, BL, lbl, WH, 8.5, '#93C5FD')
        if i < len(r1) - 1:
            _arr(ax, cx + 1.35, R1, r1[i+1][0] - 1.35, R1, BL2, 1.6)

    # bend: end of row-1 → start of row-2
    _arr(ax, 13.45, R1 - 0.39, 3.55, 5.08, PU2, 1.8, rad=-0.25)

    # row 2: agents 5–8
    R2 = 4.78
    r2 = [(2.2,  '5.  Feature\nPriority'),
          (5.5,  '6.  Opportunity\nScoring'),
          (8.8,  '7.  Roadmap\nGeneration'),
          (12.1, '8.  Executive\nReport')]
    for i, (cx, lbl) in enumerate(r2):
        _box(ax, cx, R2, 2.7, 0.78, PU, lbl, WH, 8.5, '#A78BFA')
        if i < len(r2) - 1:
            _arr(ax, cx + 1.35, R2, r2[i+1][0] - 1.35, R2, PU2, 1.6)

    _arr(ax, 8, 4.22, 8, 3.92, GR, 2.0)

    # ── OUTPUT LAYER ──────────────────────────────────────────────────────────
    _label(ax, 0.75, 3.80, 'OUTPUT LAYER', GR)
    _band(ax, 0.65, 2.80, 14.7, 0.92, GR2, '#6EE7B7')
    outs = [(2.4,  'Interactive\nDashboard'),
            (5.75, 'PDF Executive\nReport'),
            (9.1,  'Chat\nInterface'),
            (12.45,'Architecture\nDiagram')]
    for cx, lbl in outs:
        _box(ax, cx, 3.26, 2.85, 0.70, GR, lbl, WH, 8.5, '#6EE7B7')

    # ── tech stack ────────────────────────────────────────────────────────────
    ax.text(8, 2.52,
            'Python  ·  Streamlit  ·  OpenAI GPT-4o Mini  '
            '·  Pandas  ·  FPDF2  ·  Plotly  ·  Matplotlib',
            ha='center', va='center',
            fontsize=8, color=GY, style='italic', zorder=10)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150,
                bbox_inches='tight', facecolor=BG, pad_inches=0.25)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
