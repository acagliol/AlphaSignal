"use client"

import { useState, useEffect } from "react"
import { api, SectorAnalytics } from "../lib/api"

interface AnalyticsTabProps {
  refreshKey?: number
}

export default function AnalyticsTab({ refreshKey = 0 }: AnalyticsTabProps) {
  const [sectorData, setSectorData] = useState<SectorAnalytics[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const data = await api.getSectorAnalytics()
        setSectorData(data)
      } catch (error) {
        console.error("Failed to fetch analytics:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [refreshKey])

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`
    return `$${(value / 1000).toFixed(0)}K`
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
      display: "flex",
      flexDirection: "column" as const,
      gap: "1.5rem",
    },
    title: {
      fontSize: "1.5rem",
      fontWeight: "bold",
      color: "#00ff9d",
      marginBottom: "1.5rem",
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    sectorCard: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "1.5rem",
      transition: "all 0.3s",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
  }

  if (loading) {
    return <div style={styles.loadingContainer}>⏳ Loading Analytics...</div>
  }

  if (sectorData.length === 0) {
    return (
      <div style={styles.noDataContainer}>
        <h2 style={styles.noDataTitle}>🔍 NO ANALYTICS DATA</h2>
        <p>Load portfolio data to view sector analytics.</p>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>🎯 Sector Analytics</h2>
      {sectorData.map((sector) => {
        const returnPct = ((sector.total_current_value - sector.total_invested) / sector.total_invested) * 100

        return (
          <div key={sector.sector} style={styles.sectorCard}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
              <h3 style={{ color: "#fff", fontSize: "1.25rem", fontWeight: "bold", margin: 0 }}>
                {sector.sector}
              </h3>
              <span style={{ color: returnPct >= 0 ? "#00ff9d" : "#ff4444", fontWeight: "bold", fontSize: "1.25rem" }}>
                {returnPct >= 0 ? "+" : ""}{returnPct.toFixed(2)}%
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
              <div>
                <div style={{ fontSize: "0.75rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Invested
                </div>
                <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>
                  {formatCurrency(sector.total_invested)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: "0.75rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Current Value
                </div>
                <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>
                  {formatCurrency(sector.total_current_value)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: "0.75rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Deals
                </div>
                <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#fff", marginTop: "0.25rem" }}>
                  {sector.deal_count}
                </div>
              </div>
              <div>
                <div style={{ fontSize: "0.75rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Avg IRR
                </div>
                <div style={{
                  fontSize: "1.25rem",
                  fontWeight: "bold",
                  color: (sector.avg_irr || 0) >= 0 ? "#00ff9d" : "#ff4444",
                  marginTop: "0.25rem"
                }}>
                  {sector.avg_irr ? `${(sector.avg_irr * 100).toFixed(2)}%` : "N/A"}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
