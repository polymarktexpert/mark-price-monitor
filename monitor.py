"""Read-only mark-price monitor for Polymarket perps.

Estimates distance to maintenance margin for a fixed position using
the CLOB public price-history endpoint. No API keys, no trading.

    Equity = Collateral + unrealized PnL (at mark) - fees due - funding due
    MMR    = 0.5 / MaxLeverage

Author: Ais Fang. MIT License. Not financial advice.
"""
import asyncio
import time

import aiohttp

REST = "https://clob.polymarket.com"

# --- edit these -------------------------------------------------------------
TOKEN_ID = "..."      # clob token id of your market
SIDE     = "BUY"      # your position side: BUY (long) or SELL (short)
SIZE     = 100.0      # position size in shares
ENTRY    = 0.62       # your average entry, in probability units
MAX_LEV  = 20.0       # market max leverage
INTERVAL = "1m"       # price-history interval: 1m, 1w, 1d, 6h, 1h, max
POLL_SEC = 5
# ----------------------------------------------------------------------------

MMR = 0.5 / MAX_LEV


def liq_distance(mark: float) -> float:
    """Distance (in prob units) from current mark to maintenance-margin line.

    Positive means the position is above the line (safe); negative means
    the naive mark-only model already puts you past it.
    """
    if SIDE == "BUY":
        equity = (mark - ENTRY) * SIZE
        floor = MMR * mark * SIZE
    else:
        equity = (ENTRY - mark) * SIZE
        floor = MMR * mark * SIZE
    return (equity - floor) / SIZE


async def poll(session: aiohttp.ClientSession) -> float | None:
    params = {"market": TOKEN_ID, "interval": INTERVAL, "fidelity": 1}
    async with session.get(f"{REST}/prices-history", params=params) as r:
        data = await r.json()
    series = data.get("history", []) if isinstance(data, dict) else data
    if not series:
        return None
    return series[-1].get("p")


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                mark = await poll(session)
                if mark is not None:
                    d = liq_distance(float(mark))
                    flag = "OK " if d > 0 else "!! "
                    print(
                        f"{time.strftime('%H:%M:%S')} {flag}mark~{float(mark):.4f} "
                        f"MMR={MMR:.3%} liq-distance={d:+.4f} prob-units"
                    )
                else:
                    print(f"{time.strftime('%H:%M:%S')} -- no data yet")
            except Exception as exc:  # noqa: BLE001 - monitor must not die
                print(f"{time.strftime('%H:%M:%S')} poll error: {exc}")
            await asyncio.sleep(POLL_SEC)


if __name__ == "__main__":
    asyncio.run(main())
