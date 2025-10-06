"use client"

import { useState, useEffect } from "react"
import { api, PortfolioKPIs, SectorAnalytics } from "../lib/api"
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

interface PortfolioTabProps {
  refreshKey?: number
}

export default function PortfolioTab({ refreshKey = 0 }: PortfolioTabProps) {
  const [portfolioData, setPortfolioData] = useState<PortfolioKPIs | null>(null)
  const [sectorData, setSectorData] = useState<SectorAnalytics[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [portfolio, sectors] = await Promise.all([
          api.getPortfolioKPIs(),
          api.getSectorAnalytics()
        ])
        setPortfolioData(portfolio)
        setSectorData(sectors)
      } catch (error) {
        console.error("Failed to fetch portfolio data:", error)
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
    if (value === null) return "N/A"
    return `${(value * 100).toFixed(2)}%`
  }

  const COLORS = ["#00ff9d", "#00cc7d", "#00995d", "#00663d", "#00331e"]

  const styles = {
    container: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "1.5rem",
    },
    metricsGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
      gap: "1.5rem",
    },
    chartsGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(500px, 1fr))",
      gap: "1.5rem",
    },
    card: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "1.5rem",
      transition: "all 0.3s",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
    cardHover: {
      borderColor: "#00ff9d",
      boxShadow: "0 0 20px rgba(0, 255, 157, 0.2)",
    },
    cardTitle: {
      fontSize: "0.75rem",
      fontWeight: "600",
      color: "#888",
      marginBottom: "0.75rem",
      margin: 0,
      textTransform: "uppercase" as const,
      letterSpacing: "0.1em",
    },
    cardValue: {
      fontSize: "2rem",
      fontWeight: "bold",
      color: "#fff",
      margin: 0,
    },
    cardChange: {
      fontSize: "0.875rem",
      fontWeight: "500",
      margin: "0.5rem 0 0 0",
      display: "flex",
      alignItems: "center",
      gap: "0.25rem",
    },
    positiveChange: {
      color: "#00ff9d",
    },
    negativeChange: {
      color: "#ff4444",
    },
    neutralChange: {
      color: "#888",
    },
    chartCard: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "1.5rem",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
    chartTitle: {
      fontSize: "1rem",
      fontWeight: "600",
      color: "#00ff9d",
      marginBottom: "1.5rem",
      margin: 0,
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    chartContainer: {
      height: "350px",
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
        ⏳ Loading Portfolio Data...
      </div>
    )
  }

  if (!portfolioData || portfolioData.active_deals === 0) {
    return (
      <div style={styles.noDataContainer}>
        <h2 style={styles.noDataTitle}>📊 NO PORTFOLIO DATA</h2>
        <p style={styles.noDataText}>
          Click "Load Portfolio Data" above to ingest sample investment data with real-time market pricing.
        </p>
      </div>
    )
  }

  // Calculate returns
  const totalReturn = portfolioData.total_current_value - portfolioData.total_invested
  const returnPercentage = (totalReturn / portfolioData.total_invested) * 100

  // Prepare sector allocation data for pie chart
  const sectorChartData = sectorData.map(sector => ({
    name: sector.sector,
    value: sector.total_current_value,
    invested: sector.total_invested,
    return: sector.total_current_value - sector.total_invested,
  }))

  return (
    <div style={styles.container}>
      {/* Key Metrics */}
      <div style={styles.metricsGrid}>
        <MetricCard
          title="Total Invested"
          value={formatCurrency(portfolioData.total_invested)}
          subtitle={`${portfolioData.active_deals} Active Deals`}
          styles={styles}
        />
        <MetricCard
          title="Current Value"
          value={formatCurrency(portfolioData.total_current_value)}
          change={formatCurrency(totalReturn)}
          isPositive={totalReturn >= 0}
          styles={styles}
        />
        <MetricCard
          title="Total Return"
          value={`${returnPercentage >= 0 ? "+" : ""}${returnPercentage.toFixed(2)}%`}
          subtitle={formatCurrency(totalReturn)}
          isPositive={returnPercentage >= 0}
          valueColor={returnPercentage >= 0 ? "#00ff9d" : "#ff4444"}
          styles={styles}
        />
        <MetricCard
          title="IRR (Internal Rate of Return)"
          value={formatPercent(portfolioData.portfolio_irr)}
          subtitle="Annualized Return"
          isPositive={(portfolioData.portfolio_irr || 0) >= 0}
          valueColor={(portfolioData.portfolio_irr || 0) >= 0 ? "#00ff9d" : "#ff4444"}
          styles={styles}
        />
        <MetricCard
          title="MOIC (Multiple on Invested Capital)"
          value={portfolioData.portfolio_moic?.toFixed(2) + "x" || "N/A"}
          subtitle="Total Value Multiple"
          styles={styles}
        />
        <MetricCard
          title="Total Distributions"
          value={formatCurrency(portfolioData.total_distributions)}
          subtitle={`DPI: ${portfolioData.portfolio_dpi?.toFixed(2) || "0.00"}x`}
          styles={styles}
        />
      </div>

      {/* Charts */}
      <div style={styles.chartsGrid}>
        {/* Sector Allocation */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>🎯 Sector Allocation</h3>
          <div style={styles.chartContainer}>
            {sectorChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sectorChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${((entry.value / portfolioData.total_current_value) * 100).toFixed(1)}%`}
                    outerRadius={120}
                    fill="#00ff9d"
                    dataKey="value"
                  >
                    {sectorChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a1a1a",
                      border: "1px solid #00ff9d",
                      borderRadius: "0.5rem",
                      color: "#fff"
                    }}
                    formatter={(value: any) => formatCurrency(value)}
                  />
                  <Legend
                    wrapperStyle={{ color: "#fff" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%", color: "#888" }}>
                No sector data available
              </div>
            )}
          </div>
        </div>

        {/* Portfolio Performance by Sector */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>📈 Sector Performance</h3>
          <div style={{ maxHeight: "350px", overflowY: "auto" }}>
            {sectorData.map((sector, index) => {
              const sectorReturn = sector.total_current_value - sector.total_invested
              const sectorReturnPct = (sectorReturn / sector.total_invested) * 100

              return (
                <div
                  key={sector.sector}
                  style={{
                    padding: "1rem",
                    marginBottom: "0.75rem",
                    backgroundColor: "#1a1a1a",
                    borderRadius: "0.5rem",
                    border: "1px solid #2a2a2a",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <span style={{ fontWeight: "600", color: "#fff" }}>{sector.sector}</span>
                    <span style={{ color: sectorReturnPct >= 0 ? "#00ff9d" : "#ff4444", fontWeight: "600" }}>
                      {sectorReturnPct >= 0 ? "+" : ""}{sectorReturnPct.toFixed(2)}%
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", color: "#888" }}>
                    <span>Invested: {formatCurrency(sector.total_invested)}</span>
                    <span>Current: {formatCurrency(sector.total_current_value)}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", color: "#888", marginTop: "0.25rem" }}>
                    <span>{sector.deal_count} Deals</span>
                    <span style={{ color: sectorReturnPct >= 0 ? "#00ff9d" : "#ff4444" }}>
                      {formatCurrency(sectorReturn)}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string
  subtitle?: string
  change?: string
  isPositive?: boolean
  valueColor?: string
  styles: any
}

function MetricCard({ title, value, subtitle, change, isPositive, valueColor, styles }: MetricCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      style={{
        ...styles.card,
        ...(isHovered ? styles.cardHover : {}),
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <p style={styles.cardTitle}>{title}</p>
      <h2 style={{
        ...styles.cardValue,
        color: valueColor || "#fff"
      }}>
        {value}
      </h2>
      {(subtitle || change) && (
        <p style={{
          ...styles.cardChange,
          ...(isPositive !== undefined
            ? isPositive
              ? styles.positiveChange
              : styles.negativeChange
            : styles.neutralChange),
        }}>
          {change && <span>{change}</span>}
          {subtitle && <span>{subtitle}</span>}
        </p>
      )}
    </div>
  )
}
