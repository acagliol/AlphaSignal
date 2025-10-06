"use client"

import { useState, useEffect } from "react"
import { api, Deal, DealKPIs } from "../lib/api"

interface DealsTabProps {
  refreshKey?: number
}

export default function DealsTab({ refreshKey = 0 }: DealsTabProps) {
  const [deals, setDeals] = useState<Deal[]>([])
  const [dealKPIs, setDealKPIs] = useState<Map<number, DealKPIs>>(new Map())
  const [loading, setLoading] = useState(true)
  const [hoveredDealId, setHoveredDealId] = useState<number | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const dealsData = await api.getDeals()
        setDeals(dealsData)

        // Fetch KPIs for each deal
        const kpisMap = new Map<number, DealKPIs>()
        await Promise.all(
          dealsData.map(async (deal) => {
            try {
              const kpis = await api.getDealKPIs(deal.id)
              kpisMap.set(deal.id, kpis)
            } catch (error) {
              console.error(`Failed to fetch KPIs for deal ${deal.id}:`, error)
            }
          })
        )
        setDealKPIs(kpisMap)
      } catch (error) {
        console.error("Failed to fetch deals:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [refreshKey])

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`
    }
    return `$${value.toFixed(2)}`
  }

  const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return "N/A"
    return `${(value * 100).toFixed(2)}%`
  }

  const styles = {
    container: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "1.5rem",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: "1rem",
    },
    title: {
      fontSize: "1.5rem",
      fontWeight: "bold",
      color: "#00ff9d",
      margin: 0,
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    dealsGrid: {
      display: "grid",
      gap: "1.5rem",
    },
    dealCard: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "1.5rem",
      transition: "all 0.3s",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
    dealCardHover: {
      borderColor: "#00ff9d",
      boxShadow: "0 0 20px rgba(0, 255, 157, 0.2)",
    },
    dealHeader: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "start",
      marginBottom: "1.5rem",
    },
    companyInfo: {
      flex: 1,
    },
    companyName: {
      fontSize: "1.25rem",
      fontWeight: "bold",
      color: "#fff",
      margin: 0,
    },
    ticker: {
      fontSize: "0.875rem",
      color: "#00ff9d",
      margin: "0.25rem 0 0 0",
      fontWeight: "600",
    },
    sector: {
      fontSize: "0.75rem",
      color: "#888",
      margin: "0.25rem 0 0 0",
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    statusBadge: {
      padding: "0.5rem 1rem",
      borderRadius: "0.5rem",
      fontSize: "0.75rem",
      fontWeight: "600",
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    metricsGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
      gap: "1.5rem",
      marginTop: "1.5rem",
      paddingTop: "1.5rem",
      borderTop: "1px solid #1a1a1a",
    },
    metric: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "0.25rem",
    },
    metricLabel: {
      fontSize: "0.75rem",
      color: "#888",
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    metricValue: {
      fontSize: "1.25rem",
      fontWeight: "bold",
      color: "#fff",
    },
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
    noDataText: {
      fontSize: "1rem",
      marginBottom: "2rem",
    },
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        ⏳ Loading Deals...
      </div>
    )
  }

  if (deals.length === 0) {
    return (
      <div style={styles.noDataContainer}>
        <h2 style={styles.noDataTitle}>💼 NO DEALS FOUND</h2>
        <p style={styles.noDataText}>
          Click "Load Portfolio Data" above to ingest sample deals with real market data.
        </p>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>📊 Active Deals ({deals.length})</h2>
      </div>

      <div style={styles.dealsGrid}>
        {deals.map((deal) => {
          const kpis = dealKPIs.get(deal.id)
          const isHovered = hoveredDealId === deal.id

          const returnPct = kpis
            ? ((kpis.current_value - kpis.invest_amount) / kpis.invest_amount) * 100
            : 0

          return (
            <div
              key={deal.id}
              style={{
                ...styles.dealCard,
                ...(isHovered ? styles.dealCardHover : {}),
              }}
              onMouseEnter={() => setHoveredDealId(deal.id)}
              onMouseLeave={() => setHoveredDealId(null)}
            >
              <div style={styles.dealHeader}>
                <div style={styles.companyInfo}>
                  <h3 style={styles.companyName}>{deal.company?.name || "Unknown Company"}</h3>
                  <p style={styles.ticker}>{deal.company?.ticker}</p>
                  <p style={styles.sector}>{deal.company?.sector}</p>
                </div>
                <div
                  style={{
                    ...styles.statusBadge,
                    backgroundColor: deal.status === "active" ? "rgba(0, 255, 157, 0.1)" : "rgba(255, 68, 68, 0.1)",
                    border: `1px solid ${deal.status === "active" ? "#00ff9d" : "#ff4444"}`,
                    color: deal.status === "active" ? "#00ff9d" : "#ff4444",
                  }}
                >
                  {deal.status}
                </div>
              </div>

              {kpis && (
                <>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "1rem", backgroundColor: "#1a1a1a", borderRadius: "0.5rem" }}>
                    <div>
                      <p style={{ fontSize: "0.75rem", color: "#888", margin: 0 }}>INVESTED</p>
                      <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#fff", margin: "0.25rem 0 0 0" }}>
                        {formatCurrency(kpis.invest_amount)}
                      </p>
                      <p style={{ fontSize: "0.75rem", color: "#888", margin: "0.25rem 0 0 0" }}>
                        {new Date(kpis.invest_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <p style={{ fontSize: "0.75rem", color: "#888", margin: 0 }}>CURRENT VALUE</p>
                      <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#fff", margin: "0.25rem 0 0 0" }}>
                        {formatCurrency(kpis.current_value)}
                      </p>
                      <p style={{ fontSize: "0.875rem", fontWeight: "600", color: returnPct >= 0 ? "#00ff9d" : "#ff4444", margin: "0.25rem 0 0 0" }}>
                        {returnPct >= 0 ? "+" : ""}{returnPct.toFixed(2)}%
                      </p>
                    </div>
                  </div>

                  <div style={styles.metricsGrid}>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>Shares</span>
                      <span style={styles.metricValue}>{kpis.shares.toFixed(2)}</span>
                    </div>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>Current Price</span>
                      <span style={styles.metricValue}>${kpis.current_price.toFixed(2)}</span>
                    </div>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>IRR</span>
                      <span style={{
                        ...styles.metricValue,
                        color: (kpis.irr || 0) >= 0 ? "#00ff9d" : "#ff4444"
                      }}>
                        {formatPercent(kpis.irr)}
                      </span>
                    </div>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>MOIC</span>
                      <span style={styles.metricValue}>
                        {kpis.moic?.toFixed(2)}x
                      </span>
                    </div>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>Distributions</span>
                      <span style={styles.metricValue}>
                        {formatCurrency(kpis.total_distributions)}
                      </span>
                    </div>
                    <div style={styles.metric}>
                      <span style={styles.metricLabel}>Unrealized Gain</span>
                      <span style={{
                        ...styles.metricValue,
                        color: kpis.unrealized_gain >= 0 ? "#00ff9d" : "#ff4444"
                      }}>
                        {formatCurrency(kpis.unrealized_gain)}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
