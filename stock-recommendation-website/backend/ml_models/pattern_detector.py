import pandas as pd
from typing import Dict, Any


class PatternDetector:
    """
    Placeholder for the custom technical pattern detector.
    Replace the logic in detect_pattern with the algorithm from the provided image.
    """

    def detect_pattern(self, historical_df: pd.DataFrame) -> Dict[str, Any]:
        if historical_df is None or historical_df.empty:
            return {"matched": False, "score": 0.0, "details": "No data"}

        try:
            df = historical_df.copy()
            # Basic sanity: need at least 50 bars
            if len(df) < 50:
                return {"matched": False, "score": 0.0, "details": "Insufficient history"}

            # Example scaffold logic (to be replaced with your image-based rules):
            # - Uptrend confirmation via 50-day > 200-day SMA
            sma_50 = df["Close"].rolling(window=50).mean()
            sma_200 = df["Close"].rolling(window=200).mean()

            trend_ok = False
            if len(sma_200.dropna()) > 0:
                trend_ok = sma_50.iloc[-1] > sma_200.iloc[-1]

            # - Recent breakout: latest close > last 20-day high
            last_20_high = df["High"].rolling(window=20).max().iloc[-2]
            latest_close = df["Close"].iloc[-1]
            breakout = latest_close > last_20_high

            # - Volume expansion: last day volume > 1.5x 20-day avg volume
            vol_20 = df["Volume"].rolling(window=20).mean().iloc[-2]
            latest_vol = df["Volume"].iloc[-1]
            volume_expansion = latest_vol > 1.5 * vol_20 if pd.notna(vol_20) else False

            score = 0
            reasons = []
            if trend_ok:
                score += 2
                reasons.append("Uptrend: 50SMA > 200SMA")
            if breakout:
                score += 2
                reasons.append("Breakout: Close > 20-day high")
            if volume_expansion:
                score += 1
                reasons.append("Volume expansion: >1.5x 20-day avg")

            matched = score >= 3
            return {
                "matched": matched,
                "score": float(score) / 5.0,
                "details": ", ".join(reasons) if reasons else "No strong signals"
            }
        except Exception as exc:
            return {"matched": False, "score": 0.0, "details": f"Error: {exc}"}


