import pandas as pd
from typing import Dict, Any
import yfinance as yf


class PatternDetector:
    """
    Placeholder for the custom technical pattern detector.
    Replace the logic in detect_pattern with the algorithm from the provided image.
    """

    def detect_pattern(self, historical_df: pd.DataFrame, symbol: str | None = None) -> Dict[str, Any]:
        if historical_df is None or historical_df.empty:
            return {"matched": False, "score": 0.0, "details": "No data"}

        try:
            df = historical_df.copy()
            # Basic sanity: need at least 50 bars
            if len(df) < 50:
                return {"matched": False, "score": 0.0, "details": "Insufficient history"}

            # Implemented rules from image:
            # rules = [
            #   price_change_52w > 0,
            #   market_cap > 1e9,
            #   current_price < 500,
            #   current_price > 100,
            #   price_vs_50dma > 100,
            #   resistance_distance < 10
            # ]

            latest_close = float(df["Close"].iloc[-1])

            # 52-week price change
            window_52w = min(252, len(df))
            price_52w_ago = float(df["Close"].iloc[-window_52w])
            price_change_52w = ((latest_close - price_52w_ago) / price_52w_ago) * 100 if price_52w_ago > 0 else 0.0

            # 50-DMA percentage vs price (current as % of 50DMA)
            dma50 = float(df["Close"].rolling(50).mean().iloc[-1]) if len(df) >= 50 else float("nan")
            price_vs_50dma = (latest_close / dma50 * 100) if pd.notna(dma50) and dma50 > 0 else 0.0

            # Simple resistance: recent 20-day high; distance in % from resistance
            recent_high = float(df["High"].rolling(20).max().iloc[-2]) if len(df) >= 21 else latest_close
            resistance_distance = ((recent_high - latest_close) / recent_high * 100) if recent_high > 0 else 100.0

            # Market cap via yfinance (if symbol available)
            market_cap = 0.0
            if symbol:
                ysym = symbol if symbol.endswith('.NS') or symbol.endswith('.BO') else f"{symbol}.NS"
                try:
                    t = yf.Ticker(ysym)
                    info = getattr(t, 'fast_info', None)
                    if info and getattr(info, 'market_cap', None):
                        market_cap = float(info.market_cap)
                    else:
                        # fallback to slower .info
                        ic = t.info
                        market_cap = float(ic.get('marketCap') or 0.0)
                except Exception:
                    market_cap = 0.0

            # Evaluate rules
            rules = [
                price_change_52w > 0.0,
                market_cap > 1e9,
                latest_close < 500.0,
                latest_close > 100.0,
                price_vs_50dma > 100.0,
                resistance_distance < 10.0,
            ]

            reasons = []
            if price_change_52w > 0.0:
                reasons.append(f"52w change positive ({price_change_52w:.1f}%)")
            if market_cap > 1e9:
                reasons.append(f"MCap>{1e9:.0f} ({market_cap:.0f})")
            if latest_close < 500.0 and latest_close > 100.0:
                reasons.append(f"Price in [100,500): {latest_close:.2f}")
            if price_vs_50dma > 100.0:
                reasons.append(f"Above 50DMA ({price_vs_50dma:.1f}% of 50DMA)")
            if resistance_distance < 10.0:
                reasons.append(f"<10% below resistance ({resistance_distance:.1f}%)")

            matched = all(rules)
            score = float(sum(1 for r in rules if r)) / len(rules)
            return {
                "matched": matched,
                "score": score,
                "details": ", ".join(reasons) if reasons else "No match",
                "metrics": {
                    "price_change_52w": price_change_52w,
                    "market_cap": market_cap,
                    "current_price": latest_close,
                    "price_vs_50dma": price_vs_50dma,
                    "resistance_distance": resistance_distance,
                }
            }
        except Exception as exc:
            return {"matched": False, "score": 0.0, "details": f"Error: {exc}"}


