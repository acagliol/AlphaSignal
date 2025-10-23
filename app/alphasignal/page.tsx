"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { TrendingUp, TrendingDown, Brain, Activity } from 'lucide-react'

interface AnalysisData {
  ticker: string
  as_of_date: string
  market_data: {
    close: number
    open: number
    high: number
    low: number
    volume: number
  }
  technical_indicators: {
    rsi_14: number | null
    macd: number | null
    macd_signal: number | null
    bb_upper: number | null
    bb_middle: number | null
    bb_lower: number | null
    volatility_10d: number | null
  }
  returns: {
    returns_1d: number | null
    returns_5d: number | null
    returns_20d: number | null
  }
  stats: {
    data_points: number
    start_date: string
    end_date: string
  }
}

interface PredictionData {
  ticker: string
  prediction_date: string
  prediction: string
  probability_up: number
  probability_down: number
  confidence: number
  message?: string
}

export default function AlphaSignalPage() {
  const [ticker, setTicker] = useState('AAPL')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<AnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionData | null>(null)
  const [predictionError, setPredictionError] = useState<string | null>(null)

  const analyzeStock = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/v1/demo/analyze/${ticker}`)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch data')
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  const generatePrediction = async () => {
    setPredictionLoading(true)
    setPredictionError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/v1/predictions/${ticker}/predict`, {
        method: 'POST',
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate prediction')
      }

      const result = await response.json()
      setPrediction(result)
    } catch (err) {
      setPredictionError(err instanceof Error ? err.message : 'An error occurred')
      setPrediction(null)
    } finally {
      setPredictionLoading(false)
    }
  }

  const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return `${(value * 100).toFixed(2)}%`
  }

  const formatNumber = (value: number | null, decimals = 2) => {
    if (value === null || value === undefined) return 'N/A'
    return value.toFixed(decimals)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500 mb-2">
            AlphaSignal
          </h1>
          <p className="text-gray-400 text-lg">
            Alternative Data Alpha Research Platform
          </p>
        </div>

        {/* Search Bar */}
        <Card className="bg-gray-800/50 border-gray-700 mb-8">
          <CardHeader>
            <CardTitle className="text-white">Analyze Stock</CardTitle>
            <CardDescription className="text-gray-400">
              Enter a ticker symbol to view technical analysis and market data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                type="text"
                placeholder="Enter ticker (e.g., AAPL, TSLA, MSFT)"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && analyzeStock()}
                className="bg-gray-900 border-gray-600 text-white placeholder-gray-500"
              />
              <Button
                onClick={analyzeStock}
                disabled={loading}
                className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700"
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Card className="bg-red-900/20 border-red-700 mb-8">
            <CardContent className="pt-6">
              <p className="text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {data && (
          <div className="space-y-6">
            {/* Market Data */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <span>{data.ticker} Market Data</span>
                  <span className="text-sm text-gray-400">As of {data.as_of_date}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Close</p>
                    <p className="text-2xl font-bold text-green-400">
                      ${formatNumber(data.market_data.close)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Open</p>
                    <p className="text-xl font-semibold text-white">
                      ${formatNumber(data.market_data.open)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">High</p>
                    <p className="text-xl font-semibold text-white">
                      ${formatNumber(data.market_data.high)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Low</p>
                    <p className="text-xl font-semibold text-white">
                      ${formatNumber(data.market_data.low)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Volume</p>
                    <p className="text-xl font-semibold text-white">
                      {data.market_data.volume.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Technical Indicators */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Technical Indicators</CardTitle>
                <CardDescription className="text-gray-400">
                  Calculated using {data.stats.data_points} data points from {data.stats.start_date} to {data.stats.end_date}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">RSI (14)</p>
                    <p className="text-3xl font-bold text-blue-400">
                      {formatNumber(data.technical_indicators.rsi_14)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {data.technical_indicators.rsi_14 && data.technical_indicators.rsi_14 > 70
                        ? 'Overbought'
                        : data.technical_indicators.rsi_14 && data.technical_indicators.rsi_14 < 30
                        ? 'Oversold'
                        : 'Neutral'}
                    </p>
                  </div>

                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">MACD</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {formatNumber(data.technical_indicators.macd, 4)}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Signal: {formatNumber(data.technical_indicators.macd_signal, 4)}
                    </p>
                  </div>

                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">Volatility (10d)</p>
                    <p className="text-2xl font-bold text-orange-400">
                      {formatPercent(data.technical_indicators.volatility_10d)}
                    </p>
                  </div>
                </div>

                <div className="mt-4 bg-gray-900/50 p-4 rounded-lg">
                  <p className="text-gray-400 text-sm mb-3">Bollinger Bands</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Upper</p>
                      <p className="text-lg font-semibold text-green-400">
                        ${formatNumber(data.technical_indicators.bb_upper)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Middle</p>
                      <p className="text-lg font-semibold text-white">
                        ${formatNumber(data.technical_indicators.bb_middle)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Lower</p>
                      <p className="text-lg font-semibold text-red-400">
                        ${formatNumber(data.technical_indicators.bb_lower)}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Returns */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Returns</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">1-Day</p>
                    <p className={`text-2xl font-bold ${data.returns.returns_1d && data.returns.returns_1d > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatPercent(data.returns.returns_1d)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">5-Day</p>
                    <p className={`text-2xl font-bold ${data.returns.returns_5d && data.returns.returns_5d > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatPercent(data.returns.returns_5d)}
                    </p>
                  </div>
                  <div className="bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">20-Day</p>
                    <p className={`text-2xl font-bold ${data.returns.returns_20d && data.returns.returns_20d > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatPercent(data.returns.returns_20d)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ML Prediction */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  ML Price Prediction
                </CardTitle>
                <CardDescription className="text-gray-400">
                  XGBoost binary classifier with 31 engineered features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button
                    onClick={generatePrediction}
                    disabled={predictionLoading}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
                  >
                    {predictionLoading ? (
                      <>
                        <Activity className="w-4 h-4 mr-2 animate-spin" />
                        Generating Prediction...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Generate Prediction
                      </>
                    )}
                  </Button>

                  {predictionError && (
                    <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                      <p className="text-red-400 text-sm">{predictionError}</p>
                    </div>
                  )}

                  {prediction && (
                    <div className="space-y-4">
                      {/* Main Prediction */}
                      <div className={`bg-gradient-to-br ${
                        prediction.prediction === 'UP'
                          ? 'from-green-900/30 to-green-800/20 border-green-700'
                          : 'from-red-900/30 to-red-800/20 border-red-700'
                      } border rounded-lg p-6`}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {prediction.prediction === 'UP' ? (
                              <TrendingUp className="w-12 h-12 text-green-400" />
                            ) : (
                              <TrendingDown className="w-12 h-12 text-red-400" />
                            )}
                            <div>
                              <p className="text-gray-400 text-sm">Direction Forecast</p>
                              <p className={`text-4xl font-bold ${
                                prediction.prediction === 'UP' ? 'text-green-400' : 'text-red-400'
                              }`}>
                                {prediction.prediction}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-gray-400 text-sm">Confidence</p>
                            <p className="text-3xl font-bold text-white">
                              {(prediction.confidence * 100).toFixed(1)}%
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {prediction.confidence > 0.7 ? 'High' : prediction.confidence > 0.6 ? 'Medium' : 'Low'}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Probabilities */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-gray-900/50 p-4 rounded-lg border border-green-800/30">
                          <p className="text-gray-400 text-sm mb-2">Probability UP</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-800 rounded-full h-3 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-green-500 to-green-400 h-full transition-all duration-500"
                                style={{ width: `${prediction.probability_up * 100}%` }}
                              />
                            </div>
                            <p className="text-lg font-bold text-green-400 w-16 text-right">
                              {(prediction.probability_up * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        <div className="bg-gray-900/50 p-4 rounded-lg border border-red-800/30">
                          <p className="text-gray-400 text-sm mb-2">Probability DOWN</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-800 rounded-full h-3 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-red-500 to-red-400 h-full transition-all duration-500"
                                style={{ width: `${prediction.probability_down * 100}%` }}
                              />
                            </div>
                            <p className="text-lg font-bold text-red-400 w-16 text-right">
                              {(prediction.probability_down * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Metadata */}
                      <div className="bg-gray-900/30 rounded-lg p-3 text-xs text-gray-500">
                        <p>Prediction Date: {prediction.prediction_date}</p>
                        <p className="mt-1">Model: XGBoost Binary Classifier (v1)</p>
                        <p className="mt-1">Features: 31 technical indicators (RSI, MACD, momentum, volatility, volume)</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>✨ Powered by AlphaSignal • Phase 1-4 Complete</p>
          <p className="mt-2">Technical Indicators (C++ 15-20x faster) • ML Predictions (XGBoost 54% accuracy)</p>
        </div>
      </div>
    </div>
  )
}
