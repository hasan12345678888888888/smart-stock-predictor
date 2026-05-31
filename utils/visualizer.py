import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    'CRITICAL': '#ff4444',
    'WARNING':  '#ffa500',
    'SAFE':     '#00cc66',
    'bg':       '#1a1a2e',
    'grid':     '#2a2a4e',
    'text':     '#e0e0e0',
    'accent':   '#e94560',
}

PRODUCT_COLORS = [
    '#00b4d8', '#e94560', '#7bed9f', '#ffa502', '#a29bfe',
    '#fd79a8', '#55efc4', '#fdcb6e', '#74b9ff', '#ff7675',
    '#6c5ce7', '#00cec9',
]


class Visualizer:
    """Plotly-based visualizations for inventory analytics."""

    def _base_layout(self, title: str) -> dict:
        return dict(
            title=dict(text=title, font=dict(color=COLORS['text'], size=16)),
            paper_bgcolor=COLORS['bg'],
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Space Grotesk'),
            xaxis=dict(gridcolor=COLORS['grid'], showgrid=True),
            yaxis=dict(gridcolor=COLORS['grid'], showgrid=True),
            legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor=COLORS['grid']),
            margin=dict(l=50, r=30, t=60, b=50),
        )

    # ── Chart 1: Daily Sales Trends ───────────────────────────────────────────
    def plot_sales_trends(self, df: pd.DataFrame) -> go.Figure:
        """Line chart of daily sales per product over 10 days."""
        day_cols = [c for c in df.columns if c.startswith('day_')]
        day_labels = [f"Day {i+1}" for i in range(len(day_cols))]

        fig = go.Figure()

        for i, (_, row) in enumerate(df.iterrows()):
            color = PRODUCT_COLORS[i % len(PRODUCT_COLORS)]
            status = row.get('status', 'SAFE')
            
            # Dashed line for critical products
            dash_style = 'dash' if status == 'CRITICAL' else 'solid'
            width = 3 if status in ('CRITICAL', 'WARNING') else 2

            y_vals = [row[c] for c in day_cols]

            fig.add_trace(go.Scatter(
                x=day_labels,
                y=y_vals,
                mode='lines+markers',
                name=row['product'],
                line=dict(color=color, width=width, dash=dash_style),
                marker=dict(size=6, color=color),
                hovertemplate=(
                    f"<b>{row['product']}</b><br>"
                    "Day: %{x}<br>"
                    "Units Sold: %{y}<extra></extra>"
                )
            ))

        layout = self._base_layout("Daily Product Sales Trends (10-Day Period)")
        layout['xaxis']['title'] = 'Day'
        layout['yaxis']['title'] = 'Units Sold'
        layout['height'] = 500
        fig.update_layout(**layout)
        return fig

    # ── Chart 2: Stock Duration Bar Chart ────────────────────────────────────
    def plot_stock_duration(self, df: pd.DataFrame, critical: int, warning: int) -> go.Figure:
        """Horizontal bar chart of days remaining per product, color-coded."""
        
        df_sorted = df.sort_values('days_remaining', ascending=True)
        
        colors = []
        for _, row in df_sorted.iterrows():
            if row['status'] == 'CRITICAL':
                colors.append(COLORS['CRITICAL'])
            elif row['status'] == 'WARNING':
                colors.append(COLORS['WARNING'])
            else:
                colors.append(COLORS['SAFE'])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df_sorted['product'],
            x=df_sorted['days_remaining'],
            orientation='h',
            marker_color=colors,
            text=df_sorted['days_remaining'].round(1).astype(str) + ' days',
            textposition='outside',
            textfont=dict(color=COLORS['text']),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Days Remaining: %{x:.1f}<br>"
                "<extra></extra>"
            )
        ))

        # Threshold lines
        fig.add_vline(x=critical, line_dash="dash", line_color=COLORS['CRITICAL'],
                      annotation_text=f"Critical ({critical}d)",
                      annotation_font_color=COLORS['CRITICAL'])
        fig.add_vline(x=warning, line_dash="dot", line_color=COLORS['WARNING'],
                      annotation_text=f"Warning ({warning}d)",
                      annotation_font_color=COLORS['WARNING'])

        layout = self._base_layout("📊 Stock Duration by Product")
        layout['xaxis']['title'] = 'Days Until Depletion'
        layout['yaxis']['title'] = ''
        layout['height'] = 500
        layout['xaxis']['range'] = [0, max(df_sorted['days_remaining'].max() * 1.2, warning * 2)]
        fig.update_layout(**layout)
        return fig

    # ── Chart 3: Depletion Forecast ───────────────────────────────────────────
    def plot_depletion_forecast(self, df: pd.DataFrame) -> go.Figure:
        """
        Area chart showing projected stock level over next 20 days.
        Shows when each product will hit zero.
        """
        forecast_days = 20
        days_x = list(range(forecast_days + 1))

        fig = go.Figure()

        for i, (_, row) in enumerate(df.iterrows()):
            color = PRODUCT_COLORS[i % len(PRODUCT_COLORS)]
            avg_daily = row['avg_daily_sales']
            stock = row['current_stock']

            projected = [max(stock - avg_daily * d, 0) for d in days_x]

            fig.add_trace(go.Scatter(
                x=days_x,
                y=projected,
                mode='lines',
                name=row['product'],
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=color.replace(')', ', 0.07)').replace('rgb', 'rgba').replace('#', 'rgba(')
                    if '#' not in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.07)",
                hovertemplate=(
                    f"<b>{row['product']}</b><br>"
                    "Day: %{x}<br>"
                    "Projected Stock: %{y:.0f} units<extra></extra>"
                )
            ))

        # Zero line
        fig.add_hline(y=0, line_dash="dot", line_color="#ff4444",
                      annotation_text="Stock Depleted", annotation_font_color="#ff4444")

        layout = self._base_layout("🔮 Projected Stock Depletion Over Next 20 Days")
        layout['xaxis']['title'] = 'Days from Today'
        layout['yaxis']['title'] = 'Projected Units Remaining'
        layout['height'] = 500
        fig.update_layout(**layout)
        return fig
