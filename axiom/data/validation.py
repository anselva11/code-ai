"""Data validation and hygiene module for market and fundamental data."""
from typing import List, Dict, Any, Tuple
import pandas as pd
from axiom.data.schemas import PriceBar

class DataValidator:
    @staticmethod
    def validate_price_bars(bars: List[PriceBar]) -> Tuple[bool, List[str]]:
        """Validates sequence of price bars for anomalies, non-positive prices, and date ordering."""
        issues = []
        if not bars:
            return False, ["Dataset kosong: tidak ada bar harga yang diterima."]

        dates = [b.date for b in bars]
        # Check monotonic ordering
        if dates != sorted(dates):
            issues.append("Urutan tanggal tidak kronologis.")

        # Check duplicates
        if len(dates) != len(set(dates)):
            issues.append(f"Ditemukan {len(dates) - len(set(dates))} tanggal duplikat.")

        non_positive = [b for b in bars if b.close <= 0 or b.high <= 0 or b.low <= 0 or b.open <= 0]
        if non_positive:
            issues.append(f"Ditemukan {len(non_positive)} bar dengan harga non-positif (<= 0).")

        high_low_violation = [b for b in bars if b.low > b.high]
        if high_low_violation:
            issues.append(f"Ditemukan {len(high_low_violation)} bar di mana Low > High.")

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Cleans dataframe, removes duplicate timestamps, forward-fills gaps, and reports hygiene metrics."""
        report = {
            "initial_rows": len(df),
            "duplicates_removed": 0,
            "missing_values_filled": 0,
            "final_rows": 0
        }
        if df.empty:
            report["final_rows"] = 0
            return df, report

        # Drop duplicate index
        initial_len = len(df)
        cleaned = df[~df.index.duplicated(keep="first")].sort_index()
        report["duplicates_removed"] = initial_len - len(cleaned)

        # Count missing values
        null_count = cleaned.isnull().sum().sum()
        report["missing_values_filled"] = int(null_count)
        cleaned = cleaned.ffill().bfill()
        report["final_rows"] = len(cleaned)

        return cleaned, report
