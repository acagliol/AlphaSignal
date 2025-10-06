"use client"

import { useState, useEffect } from "react"
import { api, Report } from "../lib/api"

interface ReportsTabProps {
  refreshKey?: number
}

export default function ReportsTab({ refreshKey = 0 }: ReportsTabProps) {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)

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

  // Show coming soon message for reports feature
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📄 Reports & Analytics</h2>

      <div style={styles.comingSoon}>
        <div style={styles.comingSoonIcon}>📊</div>
        <h3 style={styles.comingSoonTitle}>REPORT GENERATION COMING SOON</h3>
        <p style={styles.comingSoonText}>
          Automated report generation with PDF export, custom templates, and scheduled delivery
          will be available in the next release. For now, you can view all metrics in the
          Portfolio, Deals, Performance, and Analytics tabs.
        </p>
      </div>

      {reports.length > 0 && (
        <>
          <h3 style={{ ...styles.title, fontSize: "1.25rem", marginTop: "2rem" }}>Recent Reports</h3>
          {reports.map((report, index) => {
            const [isHovered, setIsHovered] = useState(false)

            return (
              <div
                key={report.id || index}
                style={{
                  ...styles.reportCard,
                  ...(isHovered ? styles.reportCardHover : {}),
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
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
