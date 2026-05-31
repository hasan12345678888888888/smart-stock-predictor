import pandas as pd
import numpy as np
from datetime import datetime


class StockAgent:
    """
    Model-Based Goal-Driven AI Agent (as described in the proposal).
    
    - Perceives: current stock levels (environment)
    - References: historical consumption patterns (internal model)
    - Evaluates: whether stock runtime hits critical/warning thresholds (goal)
    - Outputs: automated alerts with reorder recommendations
    """

    def __init__(self, critical_threshold: int = 3, warning_threshold: int = 7):
        self.critical_threshold = critical_threshold
        self.warning_threshold = warning_threshold
        self._log_lines = []
        self._log("=" * 65)
        self._log(" SMART STOCK-OUT PREDICTOR — AI AGENT INITIALIZED")
        self._log(f" Hamdard University AI Lab | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("=" * 65)

    # ── Internal Model: Perceive Environment ─────────────────────────────────

    def _perceive(self, row: pd.Series) -> dict:
        """Extract current state from environment (inventory row)."""
        day_cols = [c for c in row.index if c.startswith('day_')]
        sales_history = row[day_cols].values.astype(float)
        return {
            'product': row['product'],
            'current_stock': float(row['current_stock']),
            'sales_history': sales_history,
        }

    def _compute_consumption_rate(self, sales_history: np.ndarray) -> float:
        """
        Computes average daily consumption velocity.
        Uses weighted mean (recent days weighted more) for accuracy.
        """
        n = len(sales_history)
        weights = np.linspace(1, 2, n)  # recent days get higher weight
        weighted_avg = np.average(sales_history, weights=weights)
        return round(weighted_avg, 3)

    def _predict_days_remaining(self, current_stock: float, avg_daily: float) -> float:
        """Core prediction: how many days until stock depletes."""
        if avg_daily <= 0:
            return float('inf')
        return round(current_stock / avg_daily, 2)

    def _recommend_reorder(self, avg_daily: float, days_buffer: int = 14) -> int:
        """
        Recommends reorder quantity.
        Buffer = 14 days of average demand to avoid next stock-out.
        """
        return max(int(avg_daily * days_buffer), 1)

    # ── Goal Evaluation ───────────────────────────────────────────────────────

    def _evaluate_goal(self, days_remaining: float) -> str:
        """
        Evaluate against goal constraints:
        CRITICAL  → stock runs out within critical_threshold days
        WARNING   → stock runs out within warning_threshold days  
        SAFE      → sufficient stock
        """
        if days_remaining <= self.critical_threshold:
            return 'CRITICAL'
        elif days_remaining <= self.warning_threshold:
            return 'WARNING'
        else:
            return 'SAFE'

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        self._log_lines.append(msg)

    def get_log(self) -> str:
        return "\n".join(self._log_lines)

    # ── Main Analysis Loop ────────────────────────────────────────────────────

    def analyze(self, df: pd.DataFrame):
        """
        Main agent loop. Processes each product, runs goal evaluation,
        and produces alerts + enriched DataFrame.
        """
        alerts = []
        records = []

        self._log("\n[AGENT] Beginning inventory scan...\n")

        day_cols = [c for c in df.columns if c.startswith('day_')]
        total_days = len(day_cols)

        for _, row in df.iterrows():
            state = self._perceive(row)
            product = state['product']
            current_stock = state['current_stock']
            sales_history = state['sales_history']

            # Compute internal model
            avg_daily = self._compute_consumption_rate(sales_history)
            days_remaining = self._predict_days_remaining(current_stock, avg_daily)
            reorder_qty = self._recommend_reorder(avg_daily)

            # Evaluate goal constraint
            status = self._evaluate_goal(days_remaining)

            # Log agent output
            if status == 'CRITICAL':
                self._log(f"  [🚨 CRITICAL] {product}")
                self._log(f"    → Stock: {int(current_stock)} units | Avg daily: {avg_daily} units")
                self._log(f"    → ⚠️  Will DEPLETE in {days_remaining} days!")
                self._log(f"    → 🔄 Minimum reorder recommendation: {reorder_qty} units")
                self._log("")
                alerts.append({
                    'product': product,
                    'level': 'CRITICAL',
                    'days_remaining': days_remaining,
                    'current_stock': int(current_stock),
                    'avg_daily_sales': avg_daily,
                    'reorder_qty': reorder_qty,
                })
            elif status == 'WARNING':
                self._log(f"  [⚠️  WARNING]  {product}")
                self._log(f"    → Stock: {int(current_stock)} units | Avg daily: {avg_daily} units")
                self._log(f"    → Running low in {days_remaining} days. Consider restocking.")
                self._log(f"    → 🔄 Recommended reorder: {reorder_qty} units")
                self._log("")
                alerts.append({
                    'product': product,
                    'level': 'WARNING',
                    'days_remaining': days_remaining,
                    'current_stock': int(current_stock),
                    'avg_daily_sales': avg_daily,
                    'reorder_qty': reorder_qty,
                })
            else:
                self._log(f"  [✅ SAFE]      {product} → {days_remaining} days remaining")

            records.append({
                'product': product,
                'current_stock': int(current_stock),
                'avg_daily_sales': avg_daily,
                'days_remaining': days_remaining,
                'reorder_qty': reorder_qty,
                'status': status,
                **{col: row[col] for col in day_cols},
            })

        self._log("\n" + "=" * 65)
        self._log(f"[AGENT] Scan complete. {len(df)} products evaluated.")
        self._log(f"[AGENT] Critical alerts: {sum(1 for a in alerts if a['level']=='CRITICAL')}")
        self._log(f"[AGENT] Warning alerts:  {sum(1 for a in alerts if a['level']=='WARNING')}")
        self._log(f"[AGENT] Safe products:   {len(df) - len(alerts)}")
        self._log("=" * 65)

        df_analyzed = pd.DataFrame(records)
        return alerts, df_analyzed
