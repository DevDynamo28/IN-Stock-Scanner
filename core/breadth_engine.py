# rs_outperformance_kite_system/core/breadth_engine.py

"""Utility to evaluate overall market breadth."""

from core.breadth import evaluate_breadth


class BreadthEngine:
    """High level interface wrapping :func:`evaluate_breadth`."""

    def __init__(self, ma_days: int = 50, threshold: float = 0.55) -> None:
        self.ma_days = ma_days
        self.threshold = threshold

    def evaluate(self, stock_data_dict):
        """Return ``True`` if market breadth is strong."""
        return evaluate_breadth(stock_data_dict, self.ma_days, self.threshold)

