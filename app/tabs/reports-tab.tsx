"use client"

import { useState, useEffect } from "react"
import { api, Report, Deal, DealKPIs, PortfolioKPIs, SectorAnalytics } from "../lib/api"

interface ReportsTabProps {
  refreshKey?: number
}

export default function ReportsTab({ refreshKey = 0 }: ReportsTabProps) {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [hoveredReportId, setHoveredReportId] = useState<number | null>(null)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true)
        const data = await api.getRecentReports()
        setReports(data)
      } catch (error) {
        console.error("Failed to fetch reports:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [refreshKey])

  const downloadDealsCSV = async () => {
    try {
      setDownloading(true)

      // Fetch all deals and their KPIs
      const deals = await api.getDeals(0, 1000)
      const dealsWithKPIs = await Promise.all(
        deals.map(async (deal) => {
          try {
            const kpis = await api.getDealKPIs(deal.id)
            return { deal, kpis }
          } catch (error) {
            console.error(`Failed to fetch KPIs for deal ${deal.id}:`, error)
            return { deal, kpis: null }
          }
        })
      )

      // Create CSV headers
      const headers = [
        "Company Name",
        "Ticker",
        "Sector",
        "Currency",
        "Status",
        "Investment Date",
        "Investment Amount",
        "Shares",
        "Current Price",
        "Current Value",
        "Total Distributions",
        "Unrealized Gain",
        "Realized Gain",
        "IRR (%)",
        "MOIC",
        "DPI",
        "TVPI",
        "RVPI",
        "Return (%)",
        "As Of Date"
      ]

      // Create CSV rows
      const rows = dealsWithKPIs.map(({ deal, kpis }) => {
        const returnPct = kpis
          ? ((kpis.current_value - kpis.invest_amount) / kpis.invest_amount) * 100
          : 0

        return [
          deal.company?.name || "Unknown",
          deal.company?.ticker || "",
          deal.company?.sector || "",
          deal.company?.currency || "",
          deal.status,
          deal.invest_date,
          kpis?.invest_amount || deal.invest_amount,
          kpis?.shares || deal.shares,
          kpis?.current_price || 0,
          kpis?.current_value || 0,
          kpis?.total_distributions || 0,
          kpis?.unrealized_gain || 0,
          kpis?.realized_gain || 0,
          kpis?.irr ? (kpis.irr * 100).toFixed(2) : "N/A",
          kpis?.moic?.toFixed(2) || "N/A",
          kpis?.dpi?.toFixed(2) || "N/A",
          kpis?.tvpi?.toFixed(2) || "N/A",
          kpis?.rvpi?.toFixed(2) || "N/A",
          returnPct.toFixed(2),
          kpis?.as_of_date || new Date().toISOString().split('T')[0]
        ]
      })

      // Combine headers and rows
      const csvContent = [
        headers.join(","),
        ...rows.map(row => row.map(cell => {
          // Escape cells containing commas or quotes
          const cellStr = String(cell)
          if (cellStr.includes(",") || cellStr.includes('"') || cellStr.includes("\n")) {
            return `"${cellStr.replace(/"/g, '""')}"`
          }
          return cellStr
        }).join(","))
      ].join("\n")

      // Create download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      const timestamp = new Date().toISOString().split('T')[0]

      link.setAttribute("href", url)
      link.setAttribute("download", `deals_export_${timestamp}.csv`)
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      console.log("CSV download successful")
    } catch (error) {
      console.error("Failed to download CSV:", error)
      alert("Failed to download CSV. Please try again.")
    } finally {
      setDownloading(false)
    }
  }

  const downloadPortfolioCSV = async () => {
    try {
      setDownloading(true)

      const portfolio = await api.getPortfolioKPIs()
      const sectors = await api.getSectorAnalytics()

      // Portfolio Summary CSV
      const portfolioHeaders = ["Metric", "Value"]
      const portfolioRows = [
        ["Total Invested", `$${portfolio.total_invested.toFixed(2)}`],
        ["Total Current Value", `$${portfolio.total_current_value.toFixed(2)}`],
        ["Total Distributions", `$${portfolio.total_distributions.toFixed(2)}`],
        ["Portfolio IRR (%)", portfolio.portfolio_irr ? (portfolio.portfolio_irr * 100).toFixed(2) : "N/A"],
        ["Portfolio MOIC", portfolio.portfolio_moic?.toFixed(2) || "N/A"],
        ["Portfolio DPI", portfolio.portfolio_dpi?.toFixed(2) || "N/A"],
        ["Portfolio TVPI", portfolio.portfolio_tvpi?.toFixed(2) || "N/A"],
        ["Portfolio RVPI", portfolio.portfolio_rvpi?.toFixed(2) || "N/A"],
        ["Total Unrealized Gain", `$${portfolio.total_unrealized_gain.toFixed(2)}`],
        ["Total Realized Gain", `$${portfolio.total_realized_gain.toFixed(2)}`],
        ["Active Deals", portfolio.active_deals],
        ["Realized Deals", portfolio.realized_deals],
        ["As Of Date", portfolio.as_of_date]
      ]

      let csvContent = portfolioHeaders.join(",") + "\n"
      csvContent += portfolioRows.map(row => row.join(",")).join("\n")
      csvContent += "\n\n"

      // Sector Analytics
      csvContent += "Sector Analytics\n"
      const sectorHeaders = ["Sector", "Deal Count", "Total Invested", "Current Value", "Avg IRR (%)", "Avg MOIC", "Distributions", "Unrealized Gain", "Realized Gain"]
      csvContent += sectorHeaders.join(",") + "\n"

      sectors.forEach(sector => {
        const row = [
          sector.sector,
          sector.deal_count,
          sector.total_invested,
          sector.total_current_value,
          sector.avg_irr ? (sector.avg_irr * 100).toFixed(2) : "N/A",
          sector.avg_moic?.toFixed(2) || "N/A",
          sector.total_distributions,
          sector.unrealized_gain,
          sector.realized_gain
        ]
        csvContent += row.join(",") + "\n"
      })

      // Create download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      const timestamp = new Date().toISOString().split('T')[0]

      link.setAttribute("href", url)
      link.setAttribute("download", `portfolio_summary_${timestamp}.csv`)
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error("Failed to download portfolio CSV:", error)
      alert("Failed to download portfolio CSV. Please try again.")
    } finally {
      setDownloading(false)
    }
  }

  const styles = {
    container: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "1.5rem",
    },
    title: {
      fontSize: "1.5rem",
      fontWeight: "bold",
      color: "#00ff9d",
      margin: 0,
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    reportCard: {
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
      padding: "1.5rem",
      transition: "all 0.3s",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    },
    reportCardHover: {
      borderColor: "#00ff9d",
      boxShadow: "0 0 20px rgba(0, 255, 157, 0.2)",
    },
    reportHeader: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "start",
      marginBottom: "1rem",
    },
    reportTitle: {
      fontSize: "1.25rem",
      fontWeight: "bold",
      color: "#fff",
      margin: 0,
    },
    reportType: {
      padding: "0.5rem 1rem",
      borderRadius: "0.5rem",
      fontSize: "0.75rem",
      fontWeight: "600",
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
      backgroundColor: "rgba(0, 255, 157, 0.1)",
      border: "1px solid #00ff9d",
      color: "#00ff9d",
    },
    reportDescription: {
      fontSize: "0.875rem",
      color: "#888",
      marginBottom: "1rem",
      lineHeight: "1.5",
    },
    reportMeta: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      fontSize: "0.75rem",
      color: "#666",
      paddingTop: "1rem",
      borderTop: "1px solid #1a1a1a",
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
    comingSoon: {
      textAlign: "center" as const,
      padding: "4rem 2rem",
      backgroundColor: "#0f0f0f",
      borderRadius: "0.75rem",
      border: "1px solid #1a1a1a",
    },
    comingSoonIcon: {
      fontSize: "4rem",
      marginBottom: "1rem",
    },
    comingSoonTitle: {
      fontSize: "2rem",
      fontWeight: "bold",
      color: "#00ff9d",
      marginBottom: "1rem",
    },
    comingSoonText: {
      fontSize: "1rem",
      color: "#888",
      maxWidth: "600px",
      margin: "0 auto",
      lineHeight: "1.6",
    },
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        ⏳ Loading Reports...
      </div>
    )
  }

  const buttonStyle = {
    padding: "1rem 2rem",
    backgroundColor: "#00ff9d",
    color: "#0a0a0a",
    border: "none",
    borderRadius: "0.5rem",
    fontSize: "1rem",
    fontWeight: "bold",
    cursor: downloading ? "not-allowed" : "pointer",
    transition: "all 0.3s",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    opacity: downloading ? 0.6 : 1,
  }

  const exportSection = {
    backgroundColor: "#0f0f0f",
    borderRadius: "0.75rem",
    border: "1px solid #00ff9d",
    padding: "2rem",
    marginBottom: "2rem",
  }

  const exportTitle = {
    fontSize: "1.5rem",
    fontWeight: "bold",
    color: "#00ff9d",
    marginBottom: "1rem",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
  }

  const exportDescription = {
    fontSize: "0.875rem",
    color: "#888",
    marginBottom: "1.5rem",
    lineHeight: "1.6",
  }

  const buttonContainer = {
    display: "flex",
    gap: "1rem",
    flexWrap: "wrap" as const,
  }

  // Show export options
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📄 Reports & Exports</h2>

      <div style={exportSection}>
        <h3 style={exportTitle}>📥 Export Data</h3>
        <p style={exportDescription}>
          Download your portfolio data as CSV files. All metrics, KPIs, and analytics
          will be included with real-time market data.
        </p>
        <div style={buttonContainer}>
          <button
            onClick={downloadDealsCSV}
            disabled={downloading}
            style={buttonStyle}
            onMouseEnter={(e) => {
              if (!downloading) {
                e.currentTarget.style.transform = "translateY(-2px)"
                e.currentTarget.style.boxShadow = "0 0 20px rgba(0, 255, 157, 0.4)"
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)"
              e.currentTarget.style.boxShadow = "none"
            }}
          >
            {downloading ? "⏳ Downloading..." : "📊 Export All Deals"}
          </button>
          <button
            onClick={downloadPortfolioCSV}
            disabled={downloading}
            style={buttonStyle}
            onMouseEnter={(e) => {
              if (!downloading) {
                e.currentTarget.style.transform = "translateY(-2px)"
                e.currentTarget.style.boxShadow = "0 0 20px rgba(0, 255, 157, 0.4)"
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)"
              e.currentTarget.style.boxShadow = "none"
            }}
          >
            {downloading ? "⏳ Downloading..." : "💼 Export Portfolio Summary"}
          </button>
        </div>
      </div>

      <div style={styles.comingSoon}>
        <div style={styles.comingSoonIcon}>📊</div>
        <h3 style={styles.comingSoonTitle}>ADVANCED REPORTING COMING SOON</h3>
        <p style={styles.comingSoonText}>
          Automated PDF report generation, custom templates, scheduled delivery,
          and interactive dashboards will be available in the next release.
        </p>
      </div>

      {reports.length > 0 && (
        <>
          <h3 style={{ ...styles.title, fontSize: "1.25rem", marginTop: "2rem" }}>Recent Reports</h3>
          {reports.map((report, index) => {
            const isHovered = hoveredReportId === report.id

            return (
              <div
                key={report.id || index}
                style={{
                  ...styles.reportCard,
                  ...(isHovered ? styles.reportCardHover : {}),
                }}
                onMouseEnter={() => setHoveredReportId(report.id)}
                onMouseLeave={() => setHoveredReportId(null)}
              >
                <div style={styles.reportHeader}>
                  <h3 style={styles.reportTitle}>{report.title}</h3>
                  <div style={styles.reportType}>{report.report_type}</div>
                </div>
                <p style={styles.reportDescription}>{report.description}</p>
                <div style={styles.reportMeta}>
                  <span>Generated: {new Date(report.generated_at).toLocaleDateString()}</span>
                  <span style={{ color: "#00ff9d", textTransform: "uppercase", fontWeight: "600" }}>
                    View Report →
                  </span>
                </div>
              </div>
            )
          })}
        </>
      )}
    </div>
  )
}
