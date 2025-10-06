"use client"

import { useState, useEffect } from "react"
import PortfolioTab from "./tabs/portfolio-tab"
import DealsTab from "./tabs/deals-tab"
import PerformanceTab from "./tabs/performance-tab"
import AnalyticsTab from "./tabs/analytics-tab"
import ReportsTab from "./tabs/reports-tab"
import DataIngestion from "./components/data-ingestion"
import { api, PortfolioKPIs } from "./lib/api"

const tabs = [
  { id: "portfolio", label: "Portfolio Overview", component: PortfolioTab },
  { id: "deals", label: "Deal Pipeline", component: DealsTab },
  { id: "performance", label: "Performance", component: PerformanceTab },
  { id: "analytics", label: "Analytics", component: AnalyticsTab },
  { id: "reports", label: "Reports", component: ReportsTab },
]

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("portfolio")
  const [portfolioData, setPortfolioData] = useState<PortfolioKPIs | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    const fetchPortfolioData = async () => {
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

    fetchPortfolioData()
  }, [refreshKey])

  const handleDataIngested = () => {
    setRefreshKey(prev => prev + 1)
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`
    }
    return `$${(value / 1000).toFixed(0)}K`
  }

  const ActiveComponent = tabs.find((tab) => tab.id === activeTab)?.component || PortfolioTab

  const styles = {
    container: {
      minHeight: "100vh",
      backgroundColor: "#0a0a0a",
      fontFamily: "system-ui, -apple-system, sans-serif",
    },
    header: {
      borderBottom: "1px solid #1a1a1a",
      backgroundColor: "#0f0f0f",
      padding: "1.5rem 2rem",
      boxShadow: "0 4px 6px -1px rgba(0, 255, 157, 0.1)",
    },
    headerContent: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    },
    title: {
      fontSize: "1.75rem",
      fontWeight: "bold",
      color: "#00ff9d",
      margin: 0,
      textShadow: "0 0 20px rgba(0, 255, 157, 0.3)",
    },
    subtitle: {
      fontSize: "0.875rem",
      color: "#888",
      margin: "0.25rem 0 0 0",
    },
    headerRight: {
      display: "flex",
      alignItems: "center",
      gap: "1.5rem",
    },
    aumContainer: {
      textAlign: "right" as const,
      padding: "0.75rem 1.5rem",
      backgroundColor: "#1a1a1a",
      borderRadius: "0.5rem",
      border: "1px solid #00ff9d",
    },
    aumLabel: {
      fontSize: "0.75rem",
      fontWeight: "500",
      color: "#00ff9d",
      margin: 0,
      textTransform: "uppercase" as const,
      letterSpacing: "0.05em",
    },
    aumValue: {
      fontSize: "1.5rem",
      fontWeight: "bold",
      color: "#fff",
      margin: "0.25rem 0 0 0",
    },
    avatar: {
      height: "2.5rem",
      width: "2.5rem",
      borderRadius: "50%",
      backgroundColor: "#00ff9d",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#0a0a0a",
      fontSize: "0.875rem",
      fontWeight: "bold",
    },
    nav: {
      borderBottom: "1px solid #1a1a1a",
      backgroundColor: "#0f0f0f",
      padding: "0 2rem",
    },
    navTabs: {
      display: "flex",
      gap: "2rem",
    },
    tab: {
      padding: "1rem 0.5rem",
      borderBottom: "2px solid transparent",
      fontWeight: "500",
      fontSize: "0.875rem",
      backgroundColor: "transparent",
      border: "none",
      cursor: "pointer",
      transition: "all 0.2s",
    },
    activeTab: {
      borderBottomColor: "#00ff9d",
      color: "#00ff9d",
    },
    inactiveTab: {
      color: "#888",
    },
    main: {
      padding: "2rem",
      backgroundColor: "#0a0a0a",
    },
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div>
            <h1 style={styles.title}>PRIVATE EQUITY DASHBOARD</h1>
            <p style={styles.subtitle}>Real-Time Investment Analytics & Performance Tracking</p>
          </div>
          <div style={styles.headerRight}>
            <div style={styles.aumContainer}>
              <p style={styles.aumLabel}>Total Portfolio Value</p>
              <p style={styles.aumValue}>
                {loading ? "Loading..." : portfolioData ? formatCurrency(portfolioData.total_current_value) : "$0"}
              </p>
            </div>
            <div style={styles.avatar}>
              <span>CV</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav style={styles.nav}>
        <div style={styles.navTabs}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                ...styles.tab,
                ...(activeTab === tab.id ? styles.activeTab : styles.inactiveTab),
              }}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.color = "#00ff9d"
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.color = "#888"
                }
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main style={styles.main}>
        <DataIngestion onDataIngested={handleDataIngested} />
        <ActiveComponent refreshKey={refreshKey} />
      </main>
    </div>
  )
}
