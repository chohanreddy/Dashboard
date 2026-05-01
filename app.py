import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

st.set_page_config(
    layout="wide",
    page_title="Headcount Dashboard",
    page_icon="📊"
)

# ─── Brand colours ────────────────────────────────────────────────────────────
PRIMARY    = "#34D186"
DARK_GREEN = "#1A7A50"
LIGHT_BG   = "#EAF7F1"
COLOR_SEQ  = ["#1A7A50", "#34D186", "#3B82F6", "#F59E0B", "#8B5CF6", "#EF4444", "#94A3B8"]

st.markdown(f"""
<style>
  #MainMenu, footer {{ visibility: hidden; }}

  /* Hide sidebar entirely */
  section[data-testid="stSidebar"] {{ display: none !important; }}
  [data-testid="collapsedControl"]  {{ display: none !important; }}

  /* Tab strip */
  .stTabs [data-baseweb="tab-list"] {{
      gap: 6px;
      background: white;
      border-radius: 10px;
      padding: 5px 6px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}
  .stTabs [data-baseweb="tab"] {{
      border-radius: 7px;
      padding: 8px 18px;
      font-weight: 500;
      color: #6B7280;
  }}
  .stTabs [aria-selected="true"] {{
      background-color: {LIGHT_BG} !important;
      color: {DARK_GREEN} !important;
      font-weight: 600;
  }}

  /* KPI cards */
  .kpi-card {{
      background: white;
      border-left: 4px solid {PRIMARY};
      border-radius: 10px;
      padding: 18px 20px;
      margin-bottom: 4px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  }}
  .kpi-value {{
      font-size: 2rem;
      font-weight: 700;
      color: {DARK_GREEN};
      line-height: 1.2;
  }}
  .kpi-label {{
      font-size: 0.78rem;
      color: #6B7280;
      margin-top: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 500;
  }}
  .kpi-sub {{
      font-size: 0.78rem;
      color: #9CA3AF;
      margin-top: 2px;
  }}

  /* Scenario cards */
  .scenario-base {{
      background: linear-gradient(135deg, {LIGHT_BG} 0%, white 100%);
      border: 2px solid {PRIMARY};
      border-radius: 12px;
      padding: 24px 20px;
      text-align: center;
      box-shadow: 0 3px 10px rgba(52,209,134,0.18);
  }}
  .scenario-other {{
      background: white;
      border: 1px solid #E5E7EB;
      border-radius: 12px;
      padding: 24px 20px;
      text-align: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}

  /* Summary & dict cards */
  .summary-card {{
      background: white;
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 14px;
      border: 1px solid #E5E7EB;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .summary-card h4 {{ color: {DARK_GREEN}; margin-bottom: 8px; font-size: 1rem; }}

  .dict-card {{
      background: white;
      border-left: 3px solid {PRIMARY};
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 10px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
</style>
""", unsafe_allow_html=True)

# ─── Data loading ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    date_cols = [
        "hire_date", "contract_end_date", "confirmed_leaving_date",
        "expected_start_date", "req_opened_date",
    ]
    df = pd.read_excel(
        "hometask_dataset_People_Analyst_cleaned.xlsx",
        sheet_name="cleaned_data",
        parse_dates=date_cols,
    )
    atr = pd.read_excel(
        "hometask_dataset_People_Analyst_cleaned.xlsx",
        sheet_name="attrition",
    )
    atr = atr[atr["year_month"].astype(str).str.match(r"^\d{4}-\d{2}$", na=False)].copy()
    atr["year_month"] = pd.to_datetime(atr["year_month"], format="%Y-%m")
    atr["attrition_rate_monthly"]    = pd.to_numeric(atr["attrition_rate_monthly"],    errors="coerce")
    atr["attrition_rate_annualised"] = pd.to_numeric(atr["attrition_rate_annualised"], errors="coerce")
    return df, atr

df_all, atr_all = load_data()

# ─── Encode logo for inline HTML ─────────────────────────────────────────────

with open("Bolt_logo.svg.png", "rb") as _f:
    _logo_b64 = base64.b64encode(_f.read()).decode()

departments = sorted(df_all["department"].dropna().unique().tolist())

# ─── Top header: logo + title + filter ───────────────────────────────────────

hdr_left, hdr_right = st.columns([3, 1])

with hdr_left:
    st.markdown(f"""
    <div style="
        background: linear-gradient(100deg, {DARK_GREEN} 0%, {PRIMARY} 100%);
        padding: 18px 28px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        gap: 20px;
    ">
        <img src="data:image/png;base64,{_logo_b64}"
             style="height:44px;width:auto;filter:brightness(0) invert(1);">
        <div>
            <h1 style="color:white;margin:0;font-size:1.7rem;font-weight:700;
                       letter-spacing:-0.02em;line-height:1.2">
                Headcount Dashboard
            </h1>
            <p style="color:rgba(255,255,255,0.82);margin:4px 0 0;font-size:0.88rem">
                People Analytics &nbsp;·&nbsp; As at May 2025
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hdr_right:
    st.markdown(
        f"""<div style="
            background:white;
            border:1px solid #E5E7EB;
            border-radius:12px;
            padding:14px 16px 6px;
            box-shadow:0 1px 4px rgba(0,0,0,0.07);
            height:100%;
        ">
        <p style="margin:0 0 6px;font-size:0.75rem;font-weight:600;
                  text-transform:uppercase;letter-spacing:0.06em;color:#6B7280">
            Filter by Department
        </p>
        </div>""",
        unsafe_allow_html=True,
    )
    selected_depts = st.multiselect(
        "",
        options=departments,
        default=[],
        placeholder="All Departments",
        label_visibility="collapsed",
    )

st.markdown('<div style="margin-bottom:8px"></div>', unsafe_allow_html=True)

if selected_depts:
    df  = df_all[df_all["department"].isin(selected_depts)].copy()
    atr = atr_all[atr_all["department"].isin(selected_depts)].copy()
else:
    df  = df_all.copy()
    atr = atr_all.copy()

# ─── Pre-compute everything at top level ─────────────────────────────────────

active_df = df[df["is_active"] == 1]
open_df   = df[df["is_open"] == 1]

# KPIs – Tab 1
active_hc        = active_df["fte"].sum()
perm_fte_kpi     = active_df[active_df["employment_type"] == "FTE"]["fte"].sum()
contractors_ftc  = active_df[active_df["employment_type"] != "FTE"]["fte"].sum()
open_count       = int(df["is_open"].sum())

# KPIs – Tab 2
recruiting_n         = int((df["position_status"] == "Open - Recruiting").sum())
approved_n           = int((df["position_status"] == "Open - Approved").sum())
on_hold_n            = int((df["position_status"] == "Open - On Hold").sum())
signed_not_started_n = int(df["is_signed_not_started"].sum())

# EoY calculations
base_fte              = active_df["fte"].sum()
confirmed_leavers_fte = df[df["is_confirmed_leaver_eoy"] == 1]["fte"].sum()
ftc_fte               = df[df["is_ftc_ending_eoy"] == 1]["fte"].sum()
overlap_fte           = df[
    (df["is_confirmed_leaver_eoy"] == 1) & (df["is_ftc_ending_eoy"] == 1)
]["fte"].sum()
net_exits     = confirmed_leavers_fte + ftc_fte - overlap_fte
starters_fte  = df[df["is_open_with_offer"] == 1]["fte"].sum()
net_confirmed = base_fte - net_exits + starters_fte
stable_fte    = df[
    (df["is_active"] == 1) &
    (df["employment_type"] == "FTE") &
    (df["is_confirmed_leaver_eoy"] == 0)
]["fte"].sum()

scenarios = {}
for _name, _rate in [("Low", 0.12), ("Base", 0.15), ("High", 0.18)]:
    _vol = stable_fte * _rate * (8 / 12)
    scenarios[_name] = {"rate": _rate, "vol_attr": _vol, "eoy": round(net_confirmed - _vol, 1)}

pending_budget = int((open_df["budget_owner_approval"] != "Approved").sum()) if not open_df.empty else 0

# ─── Helpers ─────────────────────────────────────────────────────────────────

def kpi_card(col, label, value, sub=None):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )

def clean_chart(fig, height=380, legend_h=True):
    leg = (
        dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5)
        if legend_h else dict(orientation="v")
    )
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        title_font=dict(size=14, color="#111827", family="Inter, sans-serif"),
        margin=dict(l=12, r=12, t=52, b=16),
        legend=leg,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6", zeroline=False, tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6", zeroline=False, tickfont=dict(size=11))
    return fig

def add_donut_center(fig, total, unit="FTE"):
    fig.add_annotation(
        text=(
            f"<b style='font-size:20px;color:{DARK_GREEN}'>{total:,.0f}</b>"
            f"<br><span style='font-size:11px;color:#6B7280'>{unit}</span>"
        ),
        x=0.5, y=0.5,
        showarrow=False,
        xref="paper", yref="paper",
        font=dict(size=14, color=DARK_GREEN),
        align="center",
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔍 Open Positions",
    "📅 EoY Projection",
    "📝 Summary",
    "📖 Data Dictionary",
])

# ── Tab 1: Overview ───────────────────────────────────────────────────────────

with tab1:
    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Active Headcount",   f"{active_hc:,}",      "Filled positions")
    kpi_card(k2, "Permanent FTE",      f"{perm_fte_kpi:,}",   "Employment type = FTE")
    kpi_card(k3, "Contractors + FTC",  f"{contractors_ftc:,}","Non-permanent")
    kpi_card(k4, "Open Positions",     f"{open_count:,}",     "Unfilled roles")

    st.markdown("---")

    # Row 1: Active FTE by dept | by region donut
    col1, col2 = st.columns([2, 1])

    with col1:
        dept_fte = (
            active_df.groupby("department")["fte"].sum()
            .reset_index().sort_values("fte", ascending=False)
        )
        fig = px.bar(
            dept_fte, x="department", y="fte",
            title="Active FTE by Department",
            color_discrete_sequence=[DARK_GREEN],
            labels={"fte": "FTE", "department": ""},
            text="fte",
        )
        fig.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside",
            textfont=dict(size=12, color="#374151"),
            marker_line_width=0,
        )
        fig.update_layout(
            showlegend=False,
            yaxis=dict(range=[0, dept_fte["fte"].max() * 1.2]),
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with col2:
        region_fte = active_df.groupby("region")["fte"].sum().reset_index()
        fig = px.pie(
            region_fte, names="region", values="fte",
            title="Active FTE by Region",
            hole=0.60,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont_size=11,
            pull=[0.03] * len(region_fte),
        )
        add_donut_center(fig, region_fte["fte"].sum())
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    # Row 2: employment type donut | management level h-bar
    col3, col4 = st.columns([1, 2])

    with col3:
        emp_fte = active_df.groupby("employment_type")["fte"].sum().reset_index()
        fig = px.pie(
            emp_fte, names="employment_type", values="fte",
            title="Active FTE by Employment Type",
            hole=0.60,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont_size=11,
            pull=[0.03] * len(emp_fte),
        )
        add_donut_center(fig, emp_fte["fte"].sum())
        st.plotly_chart(clean_chart(fig, height=360), use_container_width=True)

    with col4:
        level_order = ["VP", "Director", "Senior Manager", "Manager", "Individual Contributor"]
        mgmt_fte = active_df.groupby("management_level")["fte"].sum().reset_index()
        mgmt_fte["management_level"] = pd.Categorical(
            mgmt_fte["management_level"], categories=level_order, ordered=True
        )
        mgmt_fte = mgmt_fte.sort_values("management_level")
        fig = px.bar(
            mgmt_fte, y="management_level", x="fte",
            orientation="h",
            title="Active FTE by Management Level",
            color_discrete_sequence=[DARK_GREEN],
            labels={"fte": "FTE", "management_level": ""},
            text="fte",
        )
        fig.update_traces(
            texttemplate="%{x:.0f}",
            textposition="outside",
            textfont=dict(size=12, color="#374151"),
            marker_line_width=0,
        )
        fig.update_layout(
            showlegend=False,
            xaxis=dict(range=[0, mgmt_fte["fte"].max() * 1.22]),
        )
        st.plotly_chart(clean_chart(fig, height=360), use_container_width=True)

    # Row 3: Grouped bar Active FTE vs Open Roles
    active_by_dept = (
        active_df.groupby("department")["fte"].sum()
        .reset_index().rename(columns={"fte": "Active FTE"})
    )
    open_by_dept = (
        open_df.groupby("department").size()
        .reset_index(name="Open Roles")
    )
    grouped = active_by_dept.merge(open_by_dept, on="department", how="outer").fillna(0)
    melted  = grouped.melt(id_vars="department", var_name="Metric", value_name="Count")

    fig = px.bar(
        melted, x="department", y="Count", color="Metric",
        barmode="group",
        title="Active FTE vs Open Roles by Department",
        color_discrete_sequence=[DARK_GREEN, "#3B82F6"],
        labels={"Count": "", "department": ""},
        text="Count",
    )
    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(size=11, color="#374151"),
        marker_line_width=0,
    )
    fig.update_layout(yaxis=dict(range=[0, melted["Count"].max() * 1.2]))
    st.plotly_chart(clean_chart(fig, height=380), use_container_width=True)

# ── Tab 2: Open Positions ─────────────────────────────────────────────────────

with tab2:
    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Actively Recruiting",  f"{recruiting_n:,}",         "Open – Recruiting")
    kpi_card(k2, "Approved Not Started", f"{approved_n:,}",           "Open – Approved")
    kpi_card(k3, "On Hold",              f"{on_hold_n:,}",            "Open – On Hold")
    kpi_card(k4, "Signed Not Started",   f"{signed_not_started_n:,}", "Offer accepted, not yet started")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        status_colors = {
            "Open - Recruiting": "#34D186",
            "Open - Approved":   "#3B82F6",
            "Open - On Hold":    "#94A3B8",
        }
        stacked = (
            open_df.groupby(["department", "position_status"])
            .size().reset_index(name="count")
        )
        stacked["label"] = stacked["count"].apply(lambda v: str(v) if v >= 2 else "")
        fig = px.bar(
            stacked, x="department", y="count", color="position_status",
            title="Open Roles by Department and Status",
            color_discrete_map=status_colors,
            labels={"count": "Open Roles", "department": "", "position_status": "Status"},
            text="label",
        )
        fig.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=11, color="white"),
            marker_line_width=0,
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with col2:
        budget_counts = open_df.groupby("budget_owner_approval").size().reset_index(name="count")
        fig = px.pie(
            budget_counts, names="budget_owner_approval", values="count",
            title="Budget Approval Status",
            hole=0.60,
            color_discrete_sequence=["#34D186", "#F59E0B", "#94A3B8"],
        )
        fig.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont_size=11,
            pull=[0.03] * len(budget_counts),
        )
        add_donut_center(fig, budget_counts["count"].sum(), unit="Open")
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    st.markdown("#### Open Roles Detail")
    table_df = (
        open_df.groupby(["department", "position_status", "budget_owner_approval"])
        .size().reset_index(name="Count")
        .rename(columns={
            "department": "Department",
            "position_status": "Status",
            "budget_owner_approval": "Budget Approval",
        })
        .sort_values(["Department", "Count"], ascending=[True, False])
    )
    st.dataframe(table_df, use_container_width=True, hide_index=True)

# ── Tab 3: EoY Projection ─────────────────────────────────────────────────────

with tab3:
    sc1, sc2, sc3 = st.columns(3)
    badges = {"Low": "Conservative", "Base": "⭐ Base Case", "High": "Pessimistic"}

    for col, (name, data) in zip([sc1, sc2, sc3], scenarios.items()):
        card_cls = "scenario-base" if name == "Base" else "scenario-other"
        delta     = data["eoy"] - base_fte
        delta_col = "#EF4444" if delta < 0 else DARK_GREEN
        delta_str = f"{'▼' if delta < 0 else '▲'} {abs(delta):.0f} vs current"
        col.markdown(
            f'<div class="{card_cls}">'
            f'<p style="color:{PRIMARY};font-size:0.72rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;margin:0 0 4px">{badges[name]}</p>'
            f'<h2 style="color:{DARK_GREEN};margin:0 0 4px;font-size:1.5rem;font-weight:700">{name}</h2>'
            f'<p style="color:#6B7280;margin:0 0 14px;font-size:0.85rem">'
            f'Attrition rate: <strong>{data["rate"]*100:.0f}%</strong></p>'
            f'<p style="font-size:2.8rem;font-weight:700;color:{DARK_GREEN};margin:0;line-height:1">'
            f'{data["eoy"]:.0f}</p>'
            f'<p style="color:#9CA3AF;font-size:0.78rem;margin:2px 0 4px">Projected EoY FTE</p>'
            f'<p style="color:{delta_col};font-size:0.82rem;font-weight:600;margin:0 0 12px">'
            f'{delta_str}</p>'
            f'<hr style="border:none;border-top:1px solid #E5E7EB;margin:0 0 12px">'
            f'<p style="color:#6B7280;font-size:0.85rem;margin:0">'
            f'Vol. attrition: <strong style="color:{DARK_GREEN}">{data["vol_attr"]:.1f} FTE</strong></p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        bar_labels = ["Current FTE", "Net Confirmed", "Low EoY", "Base EoY", "High EoY"]
        bar_values = [
            base_fte, net_confirmed,
            scenarios["Low"]["eoy"], scenarios["Base"]["eoy"], scenarios["High"]["eoy"],
        ]
        bar_colors = [DARK_GREEN, "#3B82F6", "#34D186", "#1A7A50", "#EF4444"]

        fig = go.Figure(go.Bar(
            x=bar_labels,
            y=bar_values,
            marker_color=bar_colors,
            marker_line_width=0,
            text=[f"{v:.0f}" for v in bar_values],
            textposition="outside",
            textfont=dict(size=13, color="#374151", family="Inter, sans-serif"),
        ))
        fig.update_layout(
            title="FTE Scenarios Comparison",
            title_font=dict(size=14, color="#111827", family="Inter, sans-serif"),
            yaxis=dict(
                range=[220, max(bar_values) * 1.15],
                gridcolor="#F3F4F6",
                title="FTE",
                tickfont=dict(size=11),
            ),
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            height=420,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=12, r=12, t=52, b=16),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Methodology Breakdown")
        method_df = pd.DataFrame({
            "Step": [
                "Base Active FTE",
                "− Confirmed Leavers",
                "− FTC Endings",
                "+ Overlap (double-counted)",
                "= Net Exits",
                "+ Signed Starters",
                "= Net Confirmed Position",
                "Stable FTE Base",
                "Low (12%): Vol. Attrition",
                "Base (15%): Vol. Attrition",
                "High (18%): Vol. Attrition",
            ],
            "FTE": [
                f"{base_fte:.0f}",
                f"{confirmed_leavers_fte:.0f}",
                f"{ftc_fte:.0f}",
                f"{overlap_fte:.0f}",
                f"{net_exits:.0f}",
                f"{starters_fte:.0f}",
                f"{net_confirmed:.0f}",
                f"{stable_fte:.0f}",
                f"{scenarios['Low']['vol_attr']:.1f}",
                f"{scenarios['Base']['vol_attr']:.1f}",
                f"{scenarios['High']['vol_attr']:.1f}",
            ],
        })
        st.dataframe(method_df, use_container_width=True, hide_index=True, height=430)

    st.markdown("---")

    if not atr.empty:
        # Monthly trend line
        atr_trend = (
            atr.groupby("year_month")["attrition_rate_annualised"]
            .mean().reset_index().sort_values("year_month")
        )
        avg_rate = atr_trend["attrition_rate_annualised"].mean()

        # Identify first, peak and last indices for selective labels
        _y = atr_trend["attrition_rate_annualised"] * 100
        _label_idx = sorted({0, int(_y.idxmax()), len(_y) - 1})
        _labels = [f"{v:.1f}%" if i in _label_idx else "" for i, v in enumerate(_y)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=atr_trend["year_month"],
            y=_y,
            mode="lines+markers+text",
            name="Annualised Rate",
            line=dict(color=DARK_GREEN, width=2.5),
            marker=dict(size=7, color=DARK_GREEN, line=dict(width=2, color="white")),
            text=_labels,
            textposition="top center",
            textfont=dict(size=10, color=DARK_GREEN, family="Inter, sans-serif"),
            hovertemplate="<b>%{x|%b %Y}</b><br>Annualised: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(
            y=avg_rate * 100,
            line_dash="dash",
            line_color="#EF4444",
            line_width=1.5,
            annotation_text=f"18m Avg: {avg_rate*100:.1f}%",
            annotation_position="top right",
            annotation_font=dict(color="#EF4444", size=11),
        )
        fig.update_layout(
            title="Monthly Annualised Attrition Rate",
            title_font=dict(size=14, color="#111827", family="Inter, sans-serif"),
            yaxis=dict(
                title="Annualised Rate (%)",
                tickformat=".1f",
                ticksuffix="%",
                showgrid=True,
                gridcolor="#F3F4F6",
                range=[0, atr_trend["attrition_rate_annualised"].max() * 100 * 1.35],
            ),
            xaxis=dict(showgrid=False, title=""),
            height=390,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=12),
            margin=dict(l=12, r=12, t=52, b=16),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Attrition by department
        atr_dept = (
            atr.groupby("department")["attrition_rate_annualised"]
            .mean().reset_index()
            .sort_values("attrition_rate_annualised", ascending=False)
        )
        fig = px.bar(
            atr_dept, x="department", y="attrition_rate_annualised",
            title="Average Annualised Attrition Rate by Department",
            color_discrete_sequence=[DARK_GREEN],
            labels={"attrition_rate_annualised": "Annualised Rate", "department": ""},
            text="attrition_rate_annualised",
        )
        fig.update_traces(
            texttemplate="%{text:.1%}",
            textposition="outside",
            textfont=dict(size=12, color="#374151"),
            marker_line_width=0,
        )
        fig.update_layout(
            showlegend=False,
            yaxis=dict(
                tickformat=".0%",
                range=[0, atr_dept["attrition_rate_annualised"].max() * 1.25],
            ),
        )
        st.plotly_chart(clean_chart(fig, height=360), use_container_width=True)
    else:
        st.info("No attrition data available for the selected filter.")

# ── Tab 4: Summary ────────────────────────────────────────────────────────────

with tab4:
    st.markdown("### At a Glance Summary")

    dept_fte_sum   = active_df.groupby("department")["fte"].sum()
    largest_dept   = dept_fte_sum.idxmax() if not dept_fte_sum.empty else "N/A"
    largest_dept_n = int(dept_fte_sum.max()) if not dept_fte_sum.empty else 0

    region_fte_sum   = active_df.groupby("region")["fte"].sum()
    largest_region   = region_fte_sum.idxmax() if not region_fte_sum.empty else "N/A"
    largest_region_n = int(region_fte_sum.max()) if not region_fte_sum.empty else 0

    base_eoy = int(round(scenarios["Base"]["eoy"]))
    low_eoy  = int(round(scenarios["Low"]["eoy"]))
    high_eoy = int(round(scenarios["High"]["eoy"]))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="summary-card"><h4>📍 Right Now</h4>'
            f'<p style="color:#374151;line-height:1.6">The organisation currently has '
            f'<strong>{base_fte:,} active FTE</strong>. '
            f'The largest department is <strong>{largest_dept}</strong> with {largest_dept_n} FTE, '
            f'and the largest region is <strong>{largest_region}</strong> '
            f'with {largest_region_n} FTE.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="summary-card"><h4>📅 End of Year Outlook</h4>'
            f'<p style="color:#374151;line-height:1.6">Under the '
            f'<strong>base case scenario (15% attrition)</strong>, the organisation is projected '
            f'to end the year at <strong>{base_eoy} FTE</strong>. '
            f'The range across scenarios runs from <strong>{low_eoy}</strong> (low, 12%) '
            f'to <strong>{high_eoy}</strong> (high, 18%).</p></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div class="summary-card"><h4>🔍 Hiring Pipeline</h4>'
            f'<p style="color:#374151;line-height:1.6">There are '
            f'<strong>{open_count} open positions</strong> in total. '
            f'Of these, <strong>{recruiting_n}</strong> are actively recruiting. '
            f'<strong>{pending_budget}</strong> open role(s) still need budget approval.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="summary-card"><h4>📖 How to Use This Dashboard</h4>'
            '<ol style="padding-left:18px;margin:0;color:#374151">'
            '<li style="margin-bottom:6px;line-height:1.5"><strong>Overview:</strong> Total headcount '
            'and distribution by department, region, employment type, and management level.</li>'
            '<li style="margin-bottom:6px;line-height:1.5"><strong>Open Positions:</strong> '
            'Hiring pipeline — recruiting, approved, on hold, and budget status.</li>'
            '<li style="margin-bottom:6px;line-height:1.5"><strong>EoY Projection:</strong> '
            'Year-end headcount under three attrition scenarios with full methodology.</li>'
            '<li style="margin-bottom:6px;line-height:1.5"><strong>Summary:</strong> '
            'This page — plain-language snapshot for leadership briefings.</li>'
            '<li style="line-height:1.5"><strong>Data Dictionary:</strong> '
            'Plain-English definitions for every metric.</li>'
            '</ol>'
            '<p style="margin-top:10px;font-size:0.82rem;color:#9CA3AF">'
            'Use the <strong>Department</strong> filter in the sidebar to focus any view.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

# ── Tab 5: Data Dictionary ────────────────────────────────────────────────────

with tab5:
    st.markdown("### Data Dictionary")
    st.markdown("Plain-English definitions for every metric and term used across this dashboard.")

    definitions = [
        ("Active Headcount",
         "Total FTE of employees in filled positions (is_active = 1). Includes FTE, Fixed-Term, and Contractor types."),
        ("Permanent FTE",
         "Sum of FTE for active employees on permanent contracts (employment_type = FTE)."),
        ("Stable FTE Base",
         "Active permanent FTE who are not confirmed leavers by year-end. Used as the denominator for voluntary attrition modelling."),
        ("Net Confirmed Position",
         "Projected headcount after accounting for all known exits (confirmed leavers + FTC endings) and signed starters, before voluntary attrition."),
        ("Signed Not Started",
         "Candidates who have signed an offer but not yet joined (is_signed_not_started = 1). Counted separately from active headcount."),
        ("Open - Recruiting",
         "Open positions where active recruitment is underway (position_status = 'Open - Recruiting')."),
        ("Open - Approved",
         "Positions approved to hire but recruitment not yet started (position_status = 'Open - Approved')."),
        ("Open - On Hold",
         "Positions that are approved but paused — typically due to budget review or reprioritisation (position_status = 'Open - On Hold')."),
        ("Budget Approved",
         "Open roles where the budget owner has given formal sign-off (budget_owner_approval = 'Approved')."),
        ("Confirmed Leavers",
         "Active employees with a confirmed departure date before year-end (is_confirmed_leaver_eoy = 1)."),
        ("FTC Endings",
         "Employees on Fixed-Term Contracts whose contract is due to expire before year-end (is_ftc_ending_eoy = 1)."),
        ("Voluntary Attrition",
         "Estimated unplanned departures modelled as: Stable FTE × attrition rate × (8/12 months remaining). Applied per scenario."),
        ("EoY Projection Range",
         "The range of projected year-end FTE across three attrition scenarios: Low (12%), Base (15%), and High (18%)."),
        ("FTE",
         "Full-Time Equivalent — a unit representing one full-time employee. Part-time workers may contribute a fractional FTE."),
        ("Fixed-Term",
         "An employee on a time-limited contract with a defined end date. Counted separately from permanent FTE."),
        ("Contractor",
         "An external worker engaged on a contract basis, typically through a third party. Included in active headcount but not permanent FTE."),
    ]

    col1, col2 = st.columns(2)
    mid = len(definitions) // 2 + len(definitions) % 2

    for i, (term, defn) in enumerate(definitions):
        target = col1 if i < mid else col2
        target.markdown(
            f'<div class="dict-card">'
            f'<strong style="color:{DARK_GREEN};font-size:0.95rem">{term}</strong>'
            f'<p style="margin:5px 0 0;color:#4B5563;font-size:0.88rem;line-height:1.55">{defn}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
