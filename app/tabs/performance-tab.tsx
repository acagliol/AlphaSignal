"use client"

import { useState, useEffect } from "react"
import { api, PortfolioKPIs } from "../lib/api"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

interface PerformanceTabProps {
  refreshKey?: number
}

export default function PerformanceTab({ refreshKey = 0 }: PerformanceTabProps) {
  const [portfolioData, setPortfolioData] = useState<PortfolioKPIs | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const data = await api.getPortfolioKPIs()
        setPortfolioData(data)
      } catch (error) {
        console.error("Failed to fetch portfolio data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [refreshKey])

  const formatPercent = (value: number | null) => {
    if (value === null) return "N/A"
    return `${(value * 100).toFixed(2)}%`
  }

  const styles = {
    loadingContainer: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "400px",
      color: "#00ff9d",
      fontSize: "1.5rem",
      fontWeight: "bold",
    },
    noDataContainer: {
      textAlign: "center" as const,
      padding: "3rem",
      color: "#888",
    },
    noDataTitle: {
      fontSize: "1.5rem",
      fontWeight: "bold",
      color: "#00ff9d",
      marginBottom: "1rem",
    },
    container: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
      gap: "1.5rem",
    },
    card: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "2rem",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
    title: {
      fontSize: "0.875rem",
      fontWeight: "600",
      color: "#888",
      marginBottom: "1rem",
      textTransform: "uppercase" as const,
      letterSpacing: "0.1em",
    },
    value: {
      fontSize: "2.5rem",
      fontWeight: "bold",
      color: "#00ff9d",
      marginBottom: "0.5rem",
    },
    subtitle: {
      fontSize: "0.875rem",
      color: "#888",
    },
  }

  if (loading) {
    return <div style={styles.loadingContainer}>⏳ Loading Performance Data...</div>
  }

  if (!portfolioData || portfolioData.active_deals === 0) {
    return (
      <div style={styles.noDataContainer}>
        <h2 style={styles.noDataTitle}>📈 NO PERFORMANCE DATA</h2>
        <p>Load portfolio data to view performance metrics.</p>
      </div>
    )
  }

  const metricsData = [
    { name: "IRR", value: (portfolioData.portfolio_irr || 0) * 100, label: "Internal Rate of Return" },
    { name: "MOIC", value: portfolioData.portfolio_moic || 0, label: "Multiple on Invested Capital" },
    { name: "DPI", value: portfolioData.portfolio_dpi || 0, label: "Distributed to Paid-In" },
    { name: "TVPI", value: portfolioData.portfolio_tvpi || 0, label: "Total Value to Paid-In" },
    { name: "RVPI", value: portfolioData.portfolio_rvpi || 0, label: "Residual Value to Paid-In" },
  ]

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      <div style={styles.container}>
        {metricsData.map((metric) => (
          <div key={metric.name} style={styles.card}>
            <div style={styles.title}>{metric.label}</div>
            <div style={styles.value}>
              {metric.name === "IRR" ? `${metric.value.toFixed(2)}%` : `${metric.value.toFixed(2)}x`}
            </div>
            <div style={styles.subtitle}>{metric.name}</div>
          </div>
        ))}
      </div>

      <div style={{ ...styles.card, gridColumn: "1 / -1" }}>
        <h3 style={{ ...styles.title, marginBottom: "2rem" }}>📊 Key Metrics Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={metricsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
            <XAxis dataKey="name" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1a1a1a",
                border: "1px solid #00ff9d",
                borderRadius: "0.5rem",
                color: "#fff"
              }}
            />
            <Bar dataKey="value" fill="#00ff9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
