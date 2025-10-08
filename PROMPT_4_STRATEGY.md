# Prompt 4 Frontend Strategy - Today's Focus

## Core Philosophy: **Education Over Information Overload**

With 39 backtested metrics, we need to be **strategic and pedagogical**. The goal is **learning economics**, not drowning in data.

---

## 🎯 Key Principles

### 1. **Progressive Disclosure**
- Show 5-7 core metrics immediately
- Expand to 10-15 contextual metrics on demand
- Deep dives available but not forced

### 2. **Tell a Story, Not Just Numbers**
- Connect metrics causally (Fed Rate → Mortgages → Housing)
- Highlight leading vs lagging indicators
- Explain "why this matters today"

### 3. **Weekday-Themed Focus**
- Monday: Fed & Interest Rates (7 metrics)
- Tuesday: Real Estate & Housing (8 metrics)
- Wednesday: Economic Health (10 metrics)
- Thursday: Regional & Energy (7 metrics)
- Friday: Markets & Week Summary (7 metrics)

### 4. **Smart Prioritization**
- **Always Visible**: 5 universal metrics (Fed Funds, Unemployment, S&P 500, CPI, 10Y-2Y)
- **Today's Theme**: 7-10 weekday-relevant metrics
- **On Demand**: Full 39 metrics in organized views

---

## 📊 Frontend Architecture

### Component Hierarchy

```
TodaysFocus/
├── Hero Section
│   ├── Date + Weekday Theme
│   └── "Today We're Learning About: Fed & Interest Rates"
│
├── Core Economic Dashboard (Always Visible)
│   ├── Federal Funds Rate (with sparkline)
│   ├── Unemployment Rate
│   ├── S&P 500
│   ├── CPI (Inflation)
│   └── 10Y-2Y Yield Curve (recession indicator)
│
├── Today's Deep Dive (Weekday Theme)
│   ├── Theme Explanation (educational paragraph)
│   ├── Primary Metrics (3-4 charts)
│   ├── Supporting Metrics (2-3 cards)
│   └── "What This Means" Analysis
│
├── Trending Indicators (Auto-generated)
│   ├── Biggest movers (% change)
│   ├── Historical outliers (z-score > 2)
│   └── AI-generated insights
│
└── Full Metrics Explorer (Expandable)
    ├── All 5 themes in accordion
    ├── Search/filter functionality
    └── Export/share capabilities
```

---

## 🎨 Visual Design Strategy

### 1. **Information Density Gradients**

**High Density (Core Dashboard)**
- 5 metrics in compact cards
- Sparklines for 30-day trends
- Color-coded change indicators (green/red)
- One-sentence insight per metric

**Medium Density (Today's Theme)**
- 3-4 full charts (Recharts)
- 2-3 supporting metric cards
- Educational callouts
- Relationship diagrams

**Low Density (Full Explorer)**
- Searchable table view
- Sortable columns
- Expandable row details
- Historical data access

### 2. **Educational Overlays**

```typescript
interface MetricExplanation {
  whatIsIt: string;        // "The interest rate banks charge each other"
  whyItMatters: string;    // "Sets borrowing costs across economy"
  howToRead: string;       // "Higher = more expensive to borrow"
  leadsTo: string[];       // ["Mortgage rates", "Car loans"]
  laggedBy: string[];      // ["GDP", "Employment"]
}
```

### 3. **Smart Defaults**

- **First Visit**: Show onboarding explaining weekday themes
- **Returning User**: Remember expanded/collapsed sections
- **Mobile**: Focus on Core Dashboard + Today's Theme only
- **Desktop**: Show Core + Theme + Trending by default

---

## 🧠 AI/Analytics Integration

### 1. **Automated Insights** (Use AI strategically)

```typescript
interface DailyInsight {
  type: "correlation" | "outlier" | "trend" | "threshold";
  metrics: string[];
  message: string;
  confidence: number;

  // Examples:
  // "Fed raised rates 0.25% → Mortgage rates up 0.3% (historical avg correlation: 0.87)"
  // "VIX at 18.5, up 45% this week → Market uncertainty increasing"
  // "10Y-2Y yield curve inverted (-0.2%) → Recession indicator (last 5 inversions preceded recessions)"
}
```

### 2. **Metric Relationships** (Show causality)

```typescript
const metricGraph = {
  "FEDFUNDS": {
    directly_affects: ["DFF", "DFEDTARU", "MORTGAGE30US"],
    indirectly_affects: ["HOUST", "PERMIT", "SP500"],
    lag_time: "1-3 months"
  },
  "MORTGAGE30US": {
    directly_affects: ["HOUST", "PERMIT", "UMCSENT"],
    affected_by: ["FEDFUNDS", "DGS10"],
    lag_time: "2-6 months"
  }
}
```

### 3. **Personalization** (Future enhancement)

- User selects "interests": Real Estate, Stocks, Jobs, etc.
- Reweight metrics based on interests
- Custom alerts for thresholds

---

## 🚀 Implementation Plan (Using Frontend Agent)

### Phase 1: Core Structure (Week 1)
**Agent**: `frontend`

```
Task: Create TodaysFocus page structure with:
1. Date/weekday theme hero
2. Core Economic Dashboard (5 metrics)
3. Theme-based metric display
4. Responsive mobile/desktop layouts

Components:
- MetricCard (with sparkline)
- MetricChart (Recharts line/area)
- ThemeSection (accordion/expandable)
- InsightCallout (educational boxes)

Use Shadcn/ui for: Card, Accordion, Tabs, Dialog
Use Recharts for: LineChart, AreaChart, SparklineChart
```

### Phase 2: Data Integration (Week 1)
**Agent**: `builder`

```
Task: Wire up /api/daily-metrics/daily endpoint
1. Fetch metrics for current weekday
2. Calculate % changes (day, week, month)
3. Filter by weekday theme
4. Sort by display_order

Create hooks:
- useDailyMetrics()
- useMetricHistory(code, days)
- useTrendingMetrics()
```

### Phase 3: Intelligence Layer (Week 2)
**Agent**: `frontend` + `builder`

```
Task: Add AI-powered insights
1. Z-score calculations for outlier detection
2. Correlation analysis between metrics
3. Automated insight generation
4. Historical context ("This is highest/lowest since...")

Components:
- InsightGenerator service
- MetricAnalyzer utility
- TrendingAlert component
```

### Phase 4: Polish & Education (Week 2)
**Agent**: `frontend`

```
Task: Educational enhancements
1. Metric explanation tooltips
2. Relationship diagrams
3. "Learn More" expandable sections
4. Interactive onboarding tour

Features:
- First-time user tutorial
- Metric glossary
- Economic concept explainers
- Video/article links (optional)
```

---

## 📱 Mobile-First Priorities

Since information density is crucial on mobile:

### Mobile View (< 768px)
1. **Core Dashboard Only**: 5 key metrics
2. **Swipe Cards**: Horizontal scroll for today's theme
3. **Bottom Sheet**: Full metrics explorer
4. **Minimal Charts**: Sparklines only, tap for full chart

### Tablet View (768px - 1024px)
1. Core Dashboard + Today's Theme
2. Grid layout (2 columns)
3. Trending section visible
4. Expandable full explorer

### Desktop View (> 1024px)
1. All sections visible
2. 3-column layout
3. Inline charts
4. Side-by-side comparisons

---

## 🎓 Learning-Focused Features

### 1. **Economic Concepts Library**
```
/concepts/yield-curve
/concepts/inflation
/concepts/leading-indicators
```

### 2. **Metric Relationships Visualizer**
- Force-directed graph showing metric connections
- Click metric → highlight dependencies
- Show correlation strength

### 3. **Historical Context**
- "This is highest since 2008 financial crisis"
- "Last 5 times this happened, X followed"
- Annotated timeline of major events

### 4. **Daily Summary (AI-generated)**
```
"Today's Focus: Fed & Interest Rates

The Federal Reserve's main policy rate (FEDFUNDS) remains at 5.25%,
the highest level since 2007. This high rate environment is designed
to cool inflation, which has fallen from 9.1% (June 2022) to 3.2% today.

Watch for: Mortgage rates continue climbing (7.2%), which typically
leads to reduced home sales 2-3 months later."
```

---

## 🔑 Key Metrics to Always Highlight

### **The Big 5** (Universal Economic Health)
1. **Federal Funds Rate** - Cost of money
2. **Unemployment Rate** - Job market health
3. **S&P 500** - Market sentiment
4. **CPI / PCE** - Inflation pressure
5. **10Y-2Y Yield Curve** - Recession signal

### **Weekday Spotlights**
- **Monday**: DFF (most recent Fed action)
- **Tuesday**: MORTGAGE30US (housing affordability)
- **Wednesday**: PAYEMS (jobs report)
- **Thursday**: DCOILWTICO (energy costs)
- **Friday**: VIXCLS (week's market fear level)

---

## 🚨 Red Flags to Surface

Auto-highlight when:
1. **Yield curve inverts** (10Y-2Y < 0)
2. **VIX > 30** (high fear)
3. **Unemployment spikes** (>0.3% month-over-month)
4. **Fed changes rates** (any FEDFUNDS change)
5. **High yield spreads widen** (>6%)

---

## 💡 Smart Agent Usage for Prompt 4

### Use `frontend` agent for:
- Component architecture
- Recharts visualizations
- Responsive design
- Shadcn/ui integration
- TypeScript interfaces

### Use `builder` agent for:
- API integration
- Data transformations
- Calculation logic (z-scores, % changes)
- Database queries

### Use `general-purpose` agent for:
- Research on economic concepts
- Reviewing prompt 4 requirements
- Finding examples of good economic dashboards

### **Do NOT**:
- Build everything at once
- Show all 39 metrics simultaneously
- Ignore mobile experience
- Forget educational aspect

---

## 📈 Success Criteria

✅ **User understands** what they're looking at within 10 seconds
✅ **Mobile usable** with one hand
✅ **Educational** - learns something new each visit
✅ **Not overwhelming** - progressive disclosure works
✅ **Actionable** - clear "what this means" insights
✅ **Fast** - loads in < 2 seconds
✅ **Beautiful** - information-dense but not cluttered

---

## 🎯 Next Steps

1. ✅ **Cleanup Complete**: Removed test files
2. ✅ **Documentation**: README + METRICS.md created
3. ✅ **Backtest**: 39 metrics × 5 years populated
4. 🔜 **Review Prompt 4**: Check original requirements
5. 🔜 **Launch Frontend Agent**: Build core structure
6. 🔜 **Iterate**: Educational polish

**Ready for Prompt 4 execution!** 🚀
