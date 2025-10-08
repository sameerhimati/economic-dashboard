/**
 * Weekday themes configuration for organizing metrics by category
 * Based on backend metrics_config.py
 */

export const WEEKDAY_THEMES = {
  0: 'Fed & Interest Rates',
  1: 'Real Estate & Housing',
  2: 'Economic Health',
  3: 'Regional & Energy',
  4: 'Markets & Week Summary',
  5: 'Weekly Reflection',
  6: 'Weekly Reflection',
} as const

// The Big 5 - Core Economic Indicators (always visible)
export const BIG_FIVE_METRICS = [
  'FEDFUNDS', // Federal Funds Rate
  'UNRATE', // Unemployment Rate
  'SP500', // S&P 500 Index
  'CPIAUCSL', // Consumer Price Index
  'T10Y2Y', // 10Y-2Y Treasury Spread (Yield Curve)
] as const

// Metrics grouped by weekday theme
export const WEEKDAY_METRIC_GROUPS = {
  0: [
    // Monday: Fed & Interest Rates
    'FEDFUNDS',
    'DFF',
    'DFEDTARU',
    'DGS10',
    'DGS2',
    'T10Y2Y',
    'SOFR',
  ],
  1: [
    // Tuesday: Real Estate & Housing
    'MORTGAGE30US',
    'MORTGAGE15US',
    'HOUST',
    'PERMIT',
    'UMCSENT',
    'CSUSHPINSA',
    'MSPUS',
    'RRVRUSQ156N',
  ],
  2: [
    // Wednesday: Economic Health
    'GDP',
    'UNRATE',
    'PAYEMS',
    'JTSJOL',
    'CPIAUCSL',
    'PCEPI',
    'PCEPILFE',
    'RSXFS',
    'INDPRO',
    'TCU',
  ],
  3: [
    // Thursday: Regional & Energy
    'DCOILWTICO',
    'DCOILBRENTEU',
    'GASREGW',
    'DHHNGSP',
    'CAUR',
    'TXUR',
    'NYUR',
  ],
  4: [
    // Friday: Markets & Week Summary
    'SP500',
    'DEXUSEU',
    'DEXCHUS',
    'DTWEXBGS',
    'VIXCLS',
    'BAMLH0A0HYM2',
    'T10YIE',
  ],
  5: [],
  6: [],
} as const

// Category display information
export const CATEGORY_INFO = {
  'Fed & Interest Rates': {
    icon: '💰',
    description: 'Interest rates, monetary policy, and yield curves',
    color: 'blue',
  },
  'Real Estate & Housing': {
    icon: '🏠',
    description: 'Housing market, construction, and consumer sentiment',
    color: 'green',
  },
  'Economic Health': {
    icon: '📊',
    description: 'GDP, employment, inflation, and core economic indicators',
    color: 'purple',
  },
  'Regional & Energy': {
    icon: '⚡',
    description: 'Energy prices, regional economics, and commodities',
    color: 'orange',
  },
  'Markets & Week Summary': {
    icon: '📈',
    description: 'Stock markets, currencies, volatility, and market indicators',
    color: 'red',
  },
} as const

export type WeekdayTheme = (typeof WEEKDAY_THEMES)[keyof typeof WEEKDAY_THEMES]
export type BigFiveMetric = (typeof BIG_FIVE_METRICS)[number]

/**
 * Get the theme for a specific weekday
 */
export function getThemeForWeekday(weekday: number): string {
  return WEEKDAY_THEMES[weekday as keyof typeof WEEKDAY_THEMES] || 'Economic Overview'
}

/**
 * Get metrics for a specific weekday
 */
export function getMetricsForWeekday(weekday: number): readonly string[] {
  return WEEKDAY_METRIC_GROUPS[weekday as keyof typeof WEEKDAY_METRIC_GROUPS] || []
}

/**
 * Get all metric codes
 */
export function getAllMetricCodes(): string[] {
  return Object.values(WEEKDAY_METRIC_GROUPS).flat()
}

/**
 * Check if a metric is in The Big 5
 */
export function isBigFiveMetric(code: string): boolean {
  return BIG_FIVE_METRICS.includes(code as BigFiveMetric)
}
