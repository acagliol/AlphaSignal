"use client"

import { useState, useCallback, useEffect } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, ComposedChart
} from 'recharts'

// ─── Types ────────────────────────────────────────────────────────────────────

interface HistoricalData {
  dates: string[]
  close: (number | null)[]
  open: (number | null)[]
  high: (number | null)[]
  low: (number | null)[]
  volume: number[]
  rsi: (number | null)[]
  macd: (number | null)[]
  macd_signal: (number | null)[]
  macd_histogram: (number | null)[]
  bb_upper: (number | null)[]
  bb_middle: (number | null)[]
  bb_lower: (number | null)[]
  sma20: (number | null)[]
  sma50: (number | null)[]
  sma200: (number | null)[]
  volatility: (number | null)[]
  returns_1d: (number | null)[]
  equity_bh: number[]
  equity_strategy: number[]
}

interface AnalysisData {
  ticker: string
  as_of_date: string
  market_data: { close: number; open: number; high: number; low: number; volume: number }
  technical_indicators: {
    rsi_14: number | null; macd: number | null; macd_signal: number | null
    macd_histogram: number | null; bb_upper: number | null; bb_middle: number | null
    bb_lower: number | null; volatility_10d: number | null
  }
  returns: { returns_1d: number | null; returns_5d: number | null; returns_20d: number | null }
  historical_data: HistoricalData
  feature_importance: { feature: string; importance: number }[]
  stats: {
    data_points: number; start_date: string; end_date: string
    annualized_vol: number | null; max_drawdown: number | null; sharpe_approx: number | null
  }
}

interface PredictionData {
  ticker: string; prediction_date: string; prediction: string
  probability_up: number; probability_down: number; confidence: number; message?: string
}

// ─── Constants ────────────────────────────────────────────────────────────────

const POPULAR_STOCKS = [
  { symbol: 'AAPL', name: 'Apple' },
  { symbol: 'MSFT', name: 'Microsoft' },
  { symbol: 'NVDA', name: 'NVIDIA' },
  { symbol: 'GOOGL', name: 'Alphabet' },
  { symbol: 'AMZN', name: 'Amazon' },
  { symbol: 'META', name: 'Meta' },
  { symbol: 'TSLA', name: 'Tesla' },
  { symbol: 'AMD', name: 'AMD' },
  { symbol: 'NFLX', name: 'Netflix' },
  { symbol: 'INTC', name: 'Intel' },
  { symbol: 'ADBE', name: 'Adobe' },
  { symbol: 'AVGO', name: 'Broadcom' },
]

// ─── Custom Tooltip ───────────────────────────────────────────────────────────

const TerminalTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-black border border-[#00FF00] p-2 font-mono text-[10px]">
      <p className="text-[#999999] mb-1">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}
        </p>
      ))}
    </div>
  )
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function zipHistorical(hist: HistoricalData) {
  return hist.dates.map((d, i) => ({
    date: d.slice(5),    // MM-DD
    fullDate: d,
    close: hist.close[i],
    open: hist.open[i],
    high: hist.high[i],
    low: hist.low[i],
    volume: hist.volume[i],
    rsi: hist.rsi[i],
    macd: hist.macd[i],
    macd_signal: hist.macd_signal[i],
    macd_histogram: hist.macd_histogram[i],
    bb_upper: hist.bb_upper[i],
    bb_middle: hist.bb_middle[i],
    bb_lower: hist.bb_lower[i],
    sma20: hist.sma20[i],
    sma50: hist.sma50[i],
    sma200: hist.sma200[i],
    volatility: hist.volatility[i],
    return1d: hist.returns_1d[i] != null ? (hist.returns_1d[i]! * 100) : null,
    equity_bh: hist.equity_bh[i],
    equity_strategy: hist.equity_strategy[i],
  }))
}

const fmtPct = (v: number | null) => v == null ? 'N/A' : `${(v * 100).toFixed(2)}%`
const fmtNum = (v: number | null, d = 2) => v == null ? 'N/A' : v.toFixed(d)
const fmtM = (v: number) => v >= 1e9 ? `${(v / 1e9).toFixed(1)}B` : v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v.toLocaleString()

// ─── Main Component ───────────────────────────────────────────────────────────

export default function AlphaSignalPage() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<AnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionData | null>(null)
  const [predictionError, setPredictionError] = useState<string | null>(null)
  const [activeChart, setActiveChart] = useState<'price' | 'rsi' | 'macd' | 'vol' | 'equity' | 'returns' | 'candle' | 'momentum'>('price')
  const [currentTime, setCurrentTime] = useState('')

  // Fix hydration error by setting time on client only
  useEffect(() => {
    setCurrentTime(new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString())
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const analyzeStock = useCallback(async (sym?: string) => {
    const t = (sym || ticker).toUpperCase()
    if (!t) return
    setTicker(t)
    setLoading(true)
    setError(null)
    setPrediction(null)
    setPredictionError(null)
    try {
      const res = await fetch(`http://localhost:8000/api/v1/demo/analyze/${t}?days=180`)
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Failed') }
      setData(await res.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setData(null)
    } finally { setLoading(false) }
  }, [ticker])

  const generatePrediction = async () => {
    setPredictionLoading(true)
    setPredictionError(null)
    try {
      const res = await fetch(`http://localhost:8000/api/v1/predictions/${ticker}/predict`, { method: 'POST' })
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Failed') }
      setPrediction(await res.json())
    } catch (err) {
      setPredictionError(err instanceof Error ? err.message : 'An error occurred')
    } finally { setPredictionLoading(false) }
  }

  const chartData = data ? zipHistorical(data.historical_data) : []

  // ── RSI colour ──
  const getRsiColour = (rsi: number | null) =>
    rsi == null ? 'text-gray-400' : rsi > 70 ? 'text-red-500' : rsi < 30 ? 'text-red-400' : 'text-gray-300'

  // ── Sharpe colour ──
  const getSharpeColour = (s: number | null) =>
    s == null ? 'text-gray-400' : s > 1 ? 'text-red-400' : s > 0 ? 'text-gray-300' : 'text-gray-500'

  return (
    <div className="min-h-screen bg-black font-mono text-white p-0">
      {/* ══════════════════════════════════════════════════════════════════════════ */}
      {/* COMMAND BAR */}
      {/* ══════════════════════════════════════════════════════════════════════════ */}
      <div className="fixed top-0 left-0 right-0 bg-black border-b border-[#333333] h-10 flex items-center px-4 z-50">
        <span className="text-[#00FF00] text-xs">&gt; ALPHASIGNAL</span>
        <span className="text-[#666666] text-xs ml-4">QUANTITATIVE RESEARCH TERMINAL v2.0</span>
        <div className="ml-auto text-[#666666] text-xs">
          {currentTime || '...'}
        </div>
      </div>

      <div className="pt-10">
        {/* ── Stock Selector ── */}
        {!data && (
          <div className="p-4">
            <div className="border border-[#333333] bg-black">
              {/* Header */}
              <div className="border-b border-[#333333] px-4 py-2 bg-[#111111]">
                <div className="text-[#00FF00] text-xs">══ TICKER SELECTION ══</div>
              </div>

              {/* Popular stocks grid */}
              <div className="p-4">
                <div className="text-[#999999] text-[10px] mb-3 uppercase tracking-wider">POPULAR TICKERS</div>
                <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2 mb-6">
                  {POPULAR_STOCKS.map(s => (
                    <button
                      key={s.symbol}
                      onClick={() => analyzeStock(s.symbol)}
                      disabled={loading}
                      className="border border-[#333333] bg-black hover:border-[#00FF00] hover:bg-[#001100] transition-none p-3 text-left disabled:opacity-50"
                    >
                      <div className="text-white text-xs font-bold">{s.symbol}</div>
                      <div className="text-[#666666] text-[9px] mt-1">{s.name}</div>
                    </button>
                  ))}
                </div>

                {/* Manual input */}
                <div className="border-t border-[#333333] pt-4 flex gap-2">
                  <div className="flex-1 relative">
                    <span className="absolute left-2 top-1/2 -translate-y-1/2 text-[#00FF00] text-xs">&gt;</span>
                    <input
                      placeholder="ENTER TICKER SYMBOL"
                      value={ticker}
                      onChange={e => setTicker(e.target.value.toUpperCase())}
                      onKeyDown={e => e.key === 'Enter' && ticker && analyzeStock()}
                      className="w-full bg-black border border-[#333333] text-white text-xs pl-6 pr-3 py-3 focus:outline-none focus:border-[#00FF00] font-mono placeholder-[#333333] uppercase"
                    />
                  </div>
                  <button
                    onClick={() => analyzeStock()}
                    disabled={loading || !ticker}
                    className="bg-black border border-[#00FF00] text-[#00FF00] px-6 py-3 text-xs hover:bg-[#001100] transition-none disabled:opacity-30 disabled:cursor-not-allowed uppercase tracking-wider"
                  >
                    {loading ? '[LOADING...]' : '[ANALYZE]'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Error ── */}
        {error && (
          <div className="p-4">
            <div className="border border-[#FF0000] bg-black p-3">
              <div className="text-[#FF0000] text-xs font-mono">[ERROR] {error}</div>
            </div>
          </div>
        )}

        {/* ────────────────────── DATA SECTION ────────────────────── */}
        {data && (
          <div className="p-4 space-y-0">

            {/* ══════════════════════════════════════════════════════════════════════════ */}
            {/* MARKET DATA PANEL */}
            {/* ══════════════════════════════════════════════════════════════════════════ */}
            <div className="grid grid-cols-12 gap-4">

              {/* LEFT COLUMN - TICKER INFO + PRICE DATA */}
              <div className="col-span-3 space-y-4">

                {/* Ticker Header */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">TICKER</div>
                  </div>
                  <div className="p-3">
                    <div className="text-white text-2xl font-bold tracking-wider">{data.ticker}</div>
                    <div className="text-[#666666] text-[9px] mt-1">{data.as_of_date}</div>
                  </div>
                </div>

                {/* Price Data Table */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">MARKET DATA</div>
                  </div>
                  <div className="p-0">
                    <table className="w-full text-[10px]">
                      <tbody>
                        <tr className="border-b border-[#1a1a1a]" title="Last traded price">
                          <td className="px-3 py-2 text-[#999999]">CLOSE</td>
                          <td className="px-3 py-2 text-right text-white font-bold">${fmtNum(data.market_data.close)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Opening price of the trading day">
                          <td className="px-3 py-2 text-[#999999]">OPEN</td>
                          <td className="px-3 py-2 text-right text-white">${fmtNum(data.market_data.open)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Highest price during the trading day">
                          <td className="px-3 py-2 text-[#999999]">HIGH</td>
                          <td className="px-3 py-2 text-right text-[#00FF00]">${fmtNum(data.market_data.high)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Lowest price during the trading day">
                          <td className="px-3 py-2 text-[#999999]">LOW</td>
                          <td className="px-3 py-2 text-right text-[#FF0000]">${fmtNum(data.market_data.low)}</td>
                        </tr>
                        <tr title="Total number of shares traded">
                          <td className="px-3 py-2 text-[#999999]">VOLUME</td>
                          <td className="px-3 py-2 text-right text-white">{fmtM(data.market_data.volume)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Returns */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">RETURNS</div>
                  </div>
                  <div className="p-0">
                    <table className="w-full text-[10px]">
                      <tbody>
                        <tr className="border-b border-[#1a1a1a]">
                          <td className="px-3 py-2 text-[#999999]">1D</td>
                          <td className="px-3 py-2 text-right font-bold" style={{
                            color: data.returns.returns_1d != null && data.returns.returns_1d > 0 ? '#00FF00' : '#FF0000'
                          }}>
                            {fmtPct(data.returns.returns_1d)}
                          </td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]">
                          <td className="px-3 py-2 text-[#999999]">5D</td>
                          <td className="px-3 py-2 text-right font-bold" style={{
                            color: data.returns.returns_5d != null && data.returns.returns_5d > 0 ? '#00FF00' : '#FF0000'
                          }}>
                            {fmtPct(data.returns.returns_5d)}
                          </td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 text-[#999999]">20D</td>
                          <td className="px-3 py-2 text-right font-bold" style={{
                            color: data.returns.returns_20d != null && data.returns.returns_20d > 0 ? '#00FF00' : '#FF0000'
                          }}>
                            {fmtPct(data.returns.returns_20d)}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Technical Indicators */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">TECHNICALS</div>
                  </div>
                  <div className="p-0">
                    <table className="w-full text-[10px]">
                      <tbody>
                        <tr className="border-b border-[#1a1a1a]" title="Relative Strength Index: >70 overbought, <30 oversold">
                          <td className="px-3 py-2 text-[#999999]">RSI(14)</td>
                          <td className="px-3 py-2 text-right text-white font-bold">{fmtNum(data.technical_indicators.rsi_14, 1)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Moving Average Convergence Divergence: trend-following momentum indicator">
                          <td className="px-3 py-2 text-[#999999]">MACD</td>
                          <td className="px-3 py-2 text-right text-white">{fmtNum(data.technical_indicators.macd, 4)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="MACD signal line: 9-day EMA of MACD">
                          <td className="px-3 py-2 text-[#999999]">SIGNAL</td>
                          <td className="px-3 py-2 text-right text-white">{fmtNum(data.technical_indicators.macd_signal, 4)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Bollinger Band upper bound: +2 standard deviations">
                          <td className="px-3 py-2 text-[#999999]">BB_UPPER</td>
                          <td className="px-3 py-2 text-right text-white">${fmtNum(data.technical_indicators.bb_upper)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Bollinger Band middle: 20-day SMA">
                          <td className="px-3 py-2 text-[#999999]">BB_MID</td>
                          <td className="px-3 py-2 text-right text-white">${fmtNum(data.technical_indicators.bb_middle)}</td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Bollinger Band lower bound: -2 standard deviations">
                          <td className="px-3 py-2 text-[#999999]">BB_LOWER</td>
                          <td className="px-3 py-2 text-right text-white">${fmtNum(data.technical_indicators.bb_lower)}</td>
                        </tr>
                        <tr title="10-day annualized volatility">
                          <td className="px-3 py-2 text-[#999999]">VOL(10D)</td>
                          <td className="px-3 py-2 text-right text-white">{fmtNum(data.technical_indicators.volatility_10d, 2)}%</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Quant Stats */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">QUANT METRICS</div>
                  </div>
                  <div className="p-0">
                    <table className="w-full text-[10px]">
                      <tbody>
                        <tr className="border-b border-[#1a1a1a]" title="Annualized volatility: standard deviation of returns">
                          <td className="px-3 py-2 text-[#999999]">ANN_VOL</td>
                          <td className="px-3 py-2 text-right text-white font-bold">
                            {data.stats.annualized_vol != null ? `${data.stats.annualized_vol.toFixed(1)}%` : 'N/A'}
                          </td>
                        </tr>
                        <tr className="border-b border-[#1a1a1a]" title="Maximum drawdown: largest peak-to-trough decline">
                          <td className="px-3 py-2 text-[#999999]">MAX_DD</td>
                          <td className="px-3 py-2 text-right text-[#FF0000] font-bold">
                            {data.stats.max_drawdown != null ? `${data.stats.max_drawdown.toFixed(1)}%` : 'N/A'}
                          </td>
                        </tr>
                        <tr title="Sharpe ratio: risk-adjusted return (>1 is good, >2 is excellent)">
                          <td className="px-3 py-2 text-[#999999]">SHARPE</td>
                          <td className="px-3 py-2 text-right text-white font-bold">{fmtNum(data.stats.sharpe_approx, 2)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* RIGHT COLUMN - CHARTS */}
              <div className="col-span-9 space-y-4">

                {/* Chart Navigation */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111] flex items-center justify-between">
                    <div className="text-[#00FF00] text-[10px]">CHART VIEW</div>
                    <div className="flex gap-2 flex-wrap">
                      {(['price', 'candle', 'rsi', 'macd', 'vol', 'momentum', 'equity', 'returns'] as const).map(c => (
                        <button
                          key={c}
                          onClick={() => setActiveChart(c)}
                          className={`px-3 py-1 text-[9px] border transition-none ${
                            activeChart === c
                              ? 'bg-[#00FF00] border-[#00FF00] text-black font-bold'
                              : 'bg-black border-[#333333] text-[#999999] hover:border-[#00FF00] hover:text-[#00FF00]'
                          }`}
                          title={
                            c === 'price' ? 'Price with Bollinger Bands & SMAs' :
                            c === 'candle' ? 'OHLC Candlestick Chart' :
                            c === 'rsi' ? 'Relative Strength Index (momentum oscillator)' :
                            c === 'macd' ? 'Moving Average Convergence Divergence' :
                            c === 'vol' ? 'Annualized Volatility' :
                            c === 'momentum' ? 'Price Momentum & Rate of Change' :
                            c === 'equity' ? 'Strategy Performance vs Buy & Hold' :
                            'Daily Returns Distribution'
                          }
                        >
                          {c === 'price' ? 'PRICE+BB' : c === 'candle' ? 'OHLC' : c === 'rsi' ? 'RSI' : c === 'macd' ? 'MACD' : c === 'vol' ? 'VOL' : c === 'momentum' ? 'MOM' : c === 'equity' ? 'EQUITY' : 'RETURNS'}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="h-96 bg-black">
                      <ResponsiveContainer width="100%" height="100%">
                        {activeChart === 'price' ? (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis domain={['auto', 'auto']} tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `$${v.toFixed(0)}`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <Line type="monotone" dataKey="bb_upper" stroke="#333333" strokeWidth={1} strokeDasharray="2 2" name="BB_UP" dot={false} />
                            <Line type="monotone" dataKey="bb_lower" stroke="#333333" strokeWidth={1} strokeDasharray="2 2" name="BB_LOW" dot={false} />
                            <Line type="monotone" dataKey="bb_middle" stroke="#666666" strokeWidth={1} name="BB_MID" dot={false} />
                            <Line type="monotone" dataKey="sma20" stroke="#00FF00" strokeWidth={1} name="SMA20" dot={false} />
                            <Line type="monotone" dataKey="sma50" stroke="#999999" strokeWidth={1} name="SMA50" dot={false} />
                            <Line type="monotone" dataKey="close" stroke="#FFFFFF" strokeWidth={2} name="CLOSE" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'rsi' ? (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis domain={[0, 100]} tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} />
                            <Tooltip content={<TerminalTooltip />} />
                            <ReferenceLine y={70} stroke="#FF0000" strokeDasharray="2 2" label={{ value: 'OB', fill: '#FF0000', fontSize: 9 }} />
                            <ReferenceLine y={50} stroke="#333333" strokeDasharray="2 2" />
                            <ReferenceLine y={30} stroke="#00FF00" strokeDasharray="2 2" label={{ value: 'OS', fill: '#00FF00', fontSize: 9 }} />
                            <Line type="monotone" dataKey="rsi" stroke="#00FF00" strokeWidth={2} name="RSI(14)" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'macd' ? (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} />
                            <Tooltip content={<TerminalTooltip />} />
                            <ReferenceLine y={0} stroke="#333333" />
                            <Bar dataKey="macd_histogram" name="HIST" fill="#333333" />
                            <Line type="monotone" dataKey="macd" stroke="#00FF00" strokeWidth={2} name="MACD" dot={false} />
                            <Line type="monotone" dataKey="macd_signal" stroke="#FFFFFF" strokeWidth={1} name="SIGNAL" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'vol' ? (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `${v.toFixed(0)}%`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <Line type="monotone" dataKey="volatility" stroke="#00FF00" strokeWidth={2} name="VOL_ANN%" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'candle' ? (
                          <ComposedChart data={chartData.slice(-60)} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.slice(-60).length / 8)} />
                            <YAxis domain={['auto', 'auto']} tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `$${v.toFixed(0)}`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <Bar dataKey={(d: any) => d.high != null && d.low != null ? [d.low, d.high] : null} name="HIGH-LOW" fill="#333333" />
                            <Line type="monotone" dataKey="close" stroke="#00FF00" strokeWidth={2} name="CLOSE" dot={{ fill: '#00FF00', r: 1 }} />
                            <Line type="monotone" dataKey="open" stroke="#666666" strokeWidth={1} name="OPEN" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'momentum' ? (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `${v.toFixed(1)}%`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <ReferenceLine y={0} stroke="#333333" strokeDasharray="2 2" />
                            <Area type="monotone" dataKey="return1d" fill="#00FF00" fillOpacity={0.1} stroke="#00FF00" strokeWidth={1} name="MOM_1D%" />
                            <Line type="monotone" dataKey={(d: any) => {
                              const idx = chartData.indexOf(d)
                              if (idx < 5) return null
                              const sum = chartData.slice(idx - 5, idx).reduce((acc: number, p: any) => acc + (p.return1d || 0), 0)
                              return sum / 5
                            }} stroke="#FFFFFF" strokeWidth={2} name="MOM_5D_AVG" dot={false} />
                          </ComposedChart>
                        ) : activeChart === 'equity' ? (
                          <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `${v.toFixed(0)}`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <ReferenceLine y={100} stroke="#333333" strokeDasharray="2 2" />
                            <Line type="monotone" dataKey="equity_bh" stroke="#666666" strokeWidth={1} name="BUY_HOLD" dot={false} />
                            <Line type="monotone" dataKey="equity_strategy" stroke="#00FF00" strokeWidth={2} name="STRATEGY" dot={false} />
                          </LineChart>
                        ) : (
                          <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                            <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                            <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                            <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => `${v.toFixed(1)}%`} />
                            <Tooltip content={<TerminalTooltip />} />
                            <ReferenceLine y={0} stroke="#333333" />
                            <Bar dataKey="return1d" name="RET_1D%" fill="#00FF00" />
                          </ComposedChart>
                        )}
                      </ResponsiveContainer>
                    </div>
                    <div className="text-[#666666] text-[9px] mt-2">
                      DATA POINTS: {data.stats.data_points} | PERIOD: {data.stats.start_date} - {data.stats.end_date}
                    </div>
                  </div>
                </div>

                {/* Volume Chart */}
                <div className="border border-[#333333] bg-black">
                  <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                    <div className="text-[#00FF00] text-[10px]">VOLUME PROFILE</div>
                  </div>
                  <div className="p-4">
                    <div className="h-40 bg-black">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 0, right: 5, bottom: 0, left: 5 }}>
                          <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" />
                          <XAxis dataKey="date" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} interval={Math.floor(chartData.length / 8)} />
                          <YAxis tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} tickFormatter={v => fmtM(v)} />
                          <Tooltip content={<TerminalTooltip />} />
                          <Bar dataKey="volume" name="VOL" fill="#00FF00" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ══════════════════════════════════════════════════════════════════════════ */}
            {/* ML & FEATURE IMPORTANCE PANEL */}
            {/* ══════════════════════════════════════════════════════════════════════════ */}
            <div className="grid grid-cols-2 gap-4 mt-4">

              {/* Feature Importance */}
              <div className="border border-[#333333] bg-black">
                <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                  <div className="text-[#00FF00] text-[10px]">FEATURE IMPORTANCE</div>
                </div>
                <div className="p-4">
                  {data.feature_importance.length > 0 ? (
                    <div className="h-80 bg-black">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          layout="vertical"
                          data={data.feature_importance}
                          margin={{ top: 0, right: 10, bottom: 0, left: 10 }}
                        >
                          <CartesianGrid strokeDasharray="1 1" stroke="#1a1a1a" horizontal={false} />
                          <XAxis type="number" tick={{ fill: '#666666', fontSize: 9, fontFamily: 'monospace' }} tickLine={false} />
                          <YAxis type="category" dataKey="feature" tick={{ fill: '#999999', fontSize: 8, fontFamily: 'monospace' }} tickLine={false} width={100} />
                          <Tooltip content={<TerminalTooltip />} />
                          <Bar dataKey="importance" name="IMP" fill="#00FF00" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <p className="text-[#666666] text-[10px] text-center py-8">[NO DATA AVAILABLE]</p>
                  )}
                </div>
              </div>

              {/* ML Prediction */}
              <div className="border border-[#333333] bg-black">
                <div className="border-b border-[#333333] px-3 py-2 bg-[#111111]">
                  <div className="text-[#00FF00] text-[10px]">ML PREDICTION ENGINE</div>
                </div>
                <div className="p-4 space-y-4">
                  <button
                    onClick={generatePrediction}
                    disabled={predictionLoading}
                    className="w-full bg-black border border-[#00FF00] text-[#00FF00] px-4 py-3 text-xs hover:bg-[#001100] transition-none disabled:opacity-30 disabled:cursor-not-allowed uppercase tracking-wider font-bold"
                  >
                    {predictionLoading ? '[PROCESSING...]' : '[GENERATE PREDICTION]'}
                  </button>

                  {predictionError && (
                    <div className="border border-[#FF0000] bg-black p-3">
                      <div className="text-[#FF0000] text-[10px]">[ERROR] {predictionError}</div>
                    </div>
                  )}

                  {prediction && (
                    <div className="space-y-4">
                      {/* Main prediction display */}
                      <div className="border border-[#333333] bg-black p-4">
                        <table className="w-full text-[10px]">
                          <tbody>
                            <tr className="border-b border-[#1a1a1a]">
                              <td className="py-2 text-[#999999]">DIRECTION</td>
                              <td className="py-2 text-right">
                                {prediction.prediction === 'UP' ? (
                                  <span className="text-[#00FF00] font-bold flex items-center justify-end gap-1">
                                    <TrendingUp className="w-4 h-4" /> UP
                                  </span>
                                ) : (
                                  <span className="text-[#FF0000] font-bold flex items-center justify-end gap-1">
                                    <TrendingDown className="w-4 h-4" /> DOWN
                                  </span>
                                )}
                              </td>
                            </tr>
                            <tr className="border-b border-[#1a1a1a]">
                              <td className="py-2 text-[#999999]">CONFIDENCE</td>
                              <td className="py-2 text-right text-white font-bold">{(prediction.confidence * 100).toFixed(1)}%</td>
                            </tr>
                            <tr className="border-b border-[#1a1a1a]">
                              <td className="py-2 text-[#999999]">P(UP)</td>
                              <td className="py-2 text-right text-white">{(prediction.probability_up * 100).toFixed(1)}%</td>
                            </tr>
                            <tr className="border-b border-[#1a1a1a]">
                              <td className="py-2 text-[#999999]">P(DOWN)</td>
                              <td className="py-2 text-right text-white">{(prediction.probability_down * 100).toFixed(1)}%</td>
                            </tr>
                            <tr>
                              <td className="py-2 text-[#999999]">DATE</td>
                              <td className="py-2 text-right text-[#666666]">{prediction.prediction_date}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>

                      {/* Probability bars */}
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-[#999999]">PROB_UP</span>
                            <span className="text-[#00FF00]">{(prediction.probability_up * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 bg-black border border-[#333333]">
                            <div
                              className="h-full bg-[#00FF00]"
                              style={{ width: `${prediction.probability_up * 100}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-[#999999]">PROB_DOWN</span>
                            <span className="text-[#FF0000]">{(prediction.probability_down * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 bg-black border border-[#333333]">
                            <div
                              className="h-full bg-[#FF0000]"
                              style={{ width: `${prediction.probability_down * 100}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-[#999999]">CONFIDENCE</span>
                            <span className="text-white">{(prediction.confidence * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 bg-black border border-[#333333]">
                            <div
                              className="h-full bg-[#00FF00]"
                              style={{ width: `${prediction.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Signal indicator */}
                      <div className="border border-[#333333] bg-black p-3 text-center">
                        <div className="text-[#999999] text-[9px] mb-1">SIGNAL STATUS</div>
                        <div className={`text-xs font-bold ${prediction.confidence > 0.7 ? 'text-[#00FF00]' : 'text-[#999999]'}`}>
                          {prediction.confidence > 0.7 ? '[HIGH CONFIDENCE]' : prediction.confidence > 0.6 ? '[MEDIUM CONFIDENCE]' : '[LOW CONFIDENCE]'}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════════════════ */}
        {/* FOOTER */}
        {/* ══════════════════════════════════════════════════════════════════════════ */}
        <div className="mt-16 pb-6 border-t border-[#333333] pt-4 px-4">
          <div className="text-[#666666] text-[9px] font-mono text-center">
            ALPHASIGNAL TERMINAL v2.0 | NOT FINANCIAL ADVICE | FOR RESEARCH PURPOSES ONLY
          </div>
        </div>
      </div>
    </div>
  )
}
