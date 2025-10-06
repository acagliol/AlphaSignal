"use client"

import { useState } from "react"
import { api, sampleCompanies, CompanyIngest } from "../lib/api"

interface DataIngestionProps {
  onDataIngested?: () => void
}

export default function DataIngestion({ onDataIngested }: DataIngestionProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleIngestSampleData = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.ingestCompanies(sampleCompanies)
      
      if (response.success) {
        setResult(`Successfully processed ${response.companies_processed} companies. ${response.companies_failed} failed.`)
        if (response.errors.length > 0) {
          setResult(prev => prev + ` Errors: ${response.errors.join(', ')}`)
        }
        onDataIngested?.()
      } else {
        setError(`Failed to process companies: ${response.message}`)
      }
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCustomIngest = async (companies: CompanyIngest[]) => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.ingestCompanies(companies)
      
      if (response.success) {
        setResult(`Successfully processed ${response.companies_processed} companies. ${response.companies_failed} failed.`)
        if (response.errors.length > 0) {
          setResult(prev => prev + ` Errors: ${response.errors.join(', ')}`)
        }
        onDataIngested?.()
      } else {
        setError(`Failed to process companies: ${response.message}`)
      }
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={{
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #00ff9d",
      padding: "1.5rem",
      marginBottom: "1.5rem",
      boxShadow: "0 0 20px rgba(0, 255, 157, 0.1)"
    }}>
      <h3 style={{
        fontSize: "1.125rem",
        fontWeight: "600",
        color: "#00ff9d",
        marginBottom: "1rem",
        margin: 0,
        textTransform: "uppercase",
        letterSpacing: "0.05em"
      }}>
        📊 Data Ingestion
      </h3>

      <p style={{
        fontSize: "0.875rem",
        color: "#888",
        marginBottom: "1.5rem",
        margin: 0
      }}>
        Load real stock market data from Alpha Vantage API with live pricing and dividend tracking.
      </p>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <button
          onClick={handleIngestSampleData}
          disabled={isLoading}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: isLoading ? "#333" : "#00ff9d",
            color: isLoading ? "#666" : "#0a0a0a",
            border: "none",
            borderRadius: "0.5rem",
            cursor: isLoading ? "not-allowed" : "pointer",
            fontSize: "0.875rem",
            fontWeight: "600",
            transition: "all 0.2s",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = "#00cc7d"
              e.currentTarget.style.boxShadow = "0 0 20px rgba(0, 255, 157, 0.4)"
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = "#00ff9d"
              e.currentTarget.style.boxShadow = "none"
            }
          }}
        >
          {isLoading ? "⏳ Processing..." : "🚀 Load Portfolio Data"}
        </button>
      </div>

      {result && (
        <div style={{
          padding: "0.75rem",
          backgroundColor: "rgba(0, 255, 157, 0.1)",
          border: "1px solid #00ff9d",
          borderRadius: "0.5rem",
          marginBottom: "1rem"
        }}>
          <p style={{ margin: 0, fontSize: "0.875rem", color: "#00ff9d" }}>
            ✅ {result}
          </p>
        </div>
      )}

      {error && (
        <div style={{
          padding: "0.75rem",
          backgroundColor: "rgba(255, 0, 0, 0.1)",
          border: "1px solid #ff4444",
          borderRadius: "0.5rem",
          marginBottom: "1rem"
        }}>
          <p style={{ margin: 0, fontSize: "0.875rem", color: "#ff4444" }}>
            ❌ {error}
          </p>
        </div>
      )}

      <div style={{
        fontSize: "0.75rem",
        color: "#666",
        marginTop: "1rem",
        padding: "1rem",
        backgroundColor: "#1a1a1a",
        borderRadius: "0.5rem"
      }}>
        <p style={{ margin: 0, marginBottom: "0.5rem", color: "#00ff9d", fontWeight: "600" }}>
          SAMPLE PORTFOLIO:
        </p>
        <ul style={{ margin: 0, paddingLeft: "1rem" }}>
          <li>Microsoft Corp (MSFT) - $1M @ 2018-01-02</li>
          <li>Johnson & Johnson (JNJ) - $750K @ 2019-03-01</li>
          <li>JPMorgan Chase (JPM) - $500K @ 2020-06-15</li>
        </ul>
        <p style={{ margin: "0.5rem 0 0 0", color: "#888" }}>
          🔑 Real-time pricing, dividends, and IRR calculations powered by Alpha Vantage API
        </p>
      </div>
    </div>
  )
}