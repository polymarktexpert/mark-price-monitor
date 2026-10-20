# mark-price-monitor

Read-only monitor for mark vs index price divergence on Polymarket perps, with a
distance-to-liquidation estimate for a fixed position.

Author: Ais Fang — independent perps mechanics research.
Long-form breakdown: https://brainresearchhub.net/research/perps/mark-vs-index-price

## Why

The risk engine marks positions at the mark price, not the last trade:

```
Equity = Collateral + unrealized PnL (at mark) - fees due - funding due
MMR    = 0.5 / MaxLeverage      # 2.5% at 20x
```

On prediction-market perps the book can reprice much faster than the index
construction. Watching the last traded price tells you very little about where
your liquidation line actually is.

## What it does

- polls the CLOB REST endpoint for recent price history (mark proxy),
- computes distance to maintenance margin for a fixed side/size/entry,
- prints a time series you can pipe into alerts.

## Usage

```
pip install aiohttp
python monitor.py
```

Edit the constants at the top: `TOKEN_ID`, `SIDE`, `SIZE`, `ENTRY`, `MAX_LEV`.

## Files

- `monitor.py` — the monitor (asyncio + aiohttp, REST polling, no keys required)
- `LICENSE` — MIT

## Related research

- Mark vs Index Price: https://brainresearchhub.net/research/perps/mark-vs-index-price
- CLOB order book mechanics: https://brainresearchhub.net/research/perps/polymarket-clob-order-book
- Funding rate, precisely: https://brainresearchhub.net/research/perps/polymarket-perps-funding-rate

## Disclaimer

Not financial advice. Educational purposes only. Parameters change; the official
Polymarket docs are the only source of truth.
