"""
Comprehensive metrics configuration for Today's Focus.

Organizes economic indicators by weekday themes with proper API series codes.
Based on 2025 API standards for FRED, BEA, and BLS.
"""
from typing import Dict, List

# Weekday themes (0=Monday, 4=Friday, 5-6=Weekend)
WEEKDAY_THEMES = {
    0: "Fed & Interest Rates",
    1: "Real Estate & Housing",
    2: "Economic Health",
    3: "Regional & Energy",
    4: "Markets & Week Summary",
    5: "Weekly Reflection",
    6: "Weekly Reflection"
}

# Comprehensive metrics configuration
# Format: "CODE": {metadata}
METRICS_CONFIG: Dict[str, Dict] = {

    # ========== MONDAY: Fed & Interest Rates ==========
    "FEDFUNDS": {
        "display_name": "Federal Funds Rate",
        "description": "The interest rate banks charge each other for overnight loans",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 1,
        "refresh_frequency": "daily"
    },
    "DFF": {
        "display_name": "Federal Funds Effective Rate (Daily)",
        "description": "Daily effective federal funds rate",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 2,
        "refresh_frequency": "daily"
    },
    "DFEDTARU": {
        "display_name": "Fed Funds Target Range - Upper Limit",
        "description": "Upper limit of the Federal Reserve's target range for the federal funds rate",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 3,
        "refresh_frequency": "daily"
    },
    "DGS10": {
        "display_name": "10-Year Treasury Rate",
        "description": "Market yield on U.S. Treasury securities at 10-year constant maturity",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 4,
        "refresh_frequency": "daily"
    },
    "DGS2": {
        "display_name": "2-Year Treasury Rate",
        "description": "Market yield on U.S. Treasury securities at 2-year constant maturity",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 5,
        "refresh_frequency": "daily"
    },
    "T10Y2Y": {
        "display_name": "10-Year Treasury Minus 2-Year (Yield Curve)",
        "description": "Difference between 10-year and 2-year Treasury rates - key recession indicator",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 6,
        "refresh_frequency": "daily"
    },
    "SOFR": {
        "display_name": "Secured Overnight Financing Rate",
        "description": "Broad measure of the cost of borrowing cash overnight collateralized by Treasury securities",
        "source": "FRED",
        "unit": "%",
        "weekday": 0,
        "display_order": 7,
        "refresh_frequency": "daily"
    },

    # ========== TUESDAY: Real Estate & Housing ==========
    "MORTGAGE30US": {
        "display_name": "30-Year Fixed Mortgage Rate",
        "description": "Average U.S. 30-year fixed mortgage rate",
        "source": "FRED",
        "unit": "%",
        "weekday": 1,
        "display_order": 1,
        "refresh_frequency": "weekly"
    },
    "MORTGAGE15US": {
        "display_name": "15-Year Fixed Mortgage Rate",
        "description": "Average U.S. 15-year fixed mortgage rate",
        "source": "FRED",
        "unit": "%",
        "weekday": 1,
        "display_order": 2,
        "refresh_frequency": "weekly"
    },
    "HOUST": {
        "display_name": "Housing Starts",
        "description": "New privately-owned housing units started (thousands of units, annual rate)",
        "source": "FRED",
        "unit": "Thousands",
        "weekday": 1,
        "display_order": 3,
        "refresh_frequency": "monthly"
    },
    "PERMIT": {
        "display_name": "Building Permits",
        "description": "New privately-owned housing units authorized by building permits",
        "source": "FRED",
        "unit": "Thousands",
        "weekday": 1,
        "display_order": 4,
        "refresh_frequency": "monthly"
    },
    "UMCSENT": {
        "display_name": "Consumer Sentiment Index",
        "description": "University of Michigan Consumer Sentiment Index",
        "source": "FRED",
        "unit": "Index",
        "weekday": 1,
        "display_order": 5,
        "refresh_frequency": "monthly"
    },
    "CSUSHPINSA": {
        "display_name": "S&P/Case-Shiller Home Price Index",
        "description": "National home price index (not seasonally adjusted)",
        "source": "FRED",
        "unit": "Index",
        "weekday": 1,
        "display_order": 6,
        "refresh_frequency": "monthly"
    },
    "MSPUS": {
        "display_name": "Median Sales Price of Houses",
        "description": "Median sales price of houses sold in the United States",
        "source": "FRED",
        "unit": "Dollars",
        "weekday": 1,
        "display_order": 7,
        "refresh_frequency": "quarterly"
    },
    "RRVRUSQ156N": {
        "display_name": "Homeowner Vacancy Rate",
        "description": "Rental vacancy rate in the United States",
        "source": "FRED",
        "unit": "%",
        "weekday": 1,
        "display_order": 8,
        "refresh_frequency": "quarterly"
    },

    # ========== WEDNESDAY: Economic Health (GDP, Jobs, Spending) ==========
    "GDP": {
        "display_name": "Gross Domestic Product",
        "description": "Real GDP in billions of chained 2017 dollars",
        "source": "FRED",
        "unit": "Billions $",
        "weekday": 2,
        "display_order": 1,
        "refresh_frequency": "quarterly"
    },
    "UNRATE": {
        "display_name": "Unemployment Rate",
        "description": "Civilian unemployment rate",
        "source": "FRED",
        "unit": "%",
        "weekday": 2,
        "display_order": 2,
        "refresh_frequency": "monthly"
    },
    "PAYEMS": {
        "display_name": "Nonfarm Payrolls",
        "description": "All employees, total nonfarm (thousands of persons)",
        "source": "FRED",
        "unit": "Thousands",
        "weekday": 2,
        "display_order": 3,
        "refresh_frequency": "monthly"
    },
    "JTSJOL": {
        "display_name": "Job Openings (JOLTS)",
        "description": "Job openings: Total nonfarm",
        "source": "FRED",
        "unit": "Thousands",
        "weekday": 2,
        "display_order": 4,
        "refresh_frequency": "monthly"
    },
    "CPIAUCSL": {
        "display_name": "Consumer Price Index (CPI)",
        "description": "All urban consumers, all items",
        "source": "FRED",
        "unit": "Index",
        "weekday": 2,
        "display_order": 5,
        "refresh_frequency": "monthly"
    },
    "PCEPI": {
        "display_name": "PCE Price Index",
        "description": "Personal Consumption Expenditures Price Index - Fed's preferred inflation gauge",
        "source": "FRED",
        "unit": "Index",
        "weekday": 2,
        "display_order": 6,
        "refresh_frequency": "monthly"
    },
    "PCEPILFE": {
        "display_name": "Core PCE Price Index",
        "description": "Personal Consumption Expenditures excluding food and energy",
        "source": "FRED",
        "unit": "Index",
        "weekday": 2,
        "display_order": 7,
        "refresh_frequency": "monthly"
    },
    "RSXFS": {
        "display_name": "Retail Sales",
        "description": "Advance retail sales: retail and food services total",
        "source": "FRED",
        "unit": "Millions $",
        "weekday": 2,
        "display_order": 8,
        "refresh_frequency": "monthly"
    },
    "INDPRO": {
        "display_name": "Industrial Production Index",
        "description": "Industrial production: total index",
        "source": "FRED",
        "unit": "Index",
        "weekday": 2,
        "display_order": 9,
        "refresh_frequency": "monthly"
    },
    "TCU": {
        "display_name": "Capacity Utilization",
        "description": "Capacity utilization: total industry",
        "source": "FRED",
        "unit": "%",
        "weekday": 2,
        "display_order": 10,
        "refresh_frequency": "monthly"
    },

    # ========== THURSDAY: Regional & Energy ==========
    "DCOILWTICO": {
        "display_name": "Crude Oil Prices (WTI)",
        "description": "Crude oil prices: West Texas Intermediate",
        "source": "FRED",
        "unit": "$/Barrel",
        "weekday": 3,
        "display_order": 1,
        "refresh_frequency": "daily"
    },
    "DCOILBRENTEU": {
        "display_name": "Crude Oil Prices (Brent)",
        "description": "Crude oil prices: Brent - Europe",
        "source": "FRED",
        "unit": "$/Barrel",
        "weekday": 3,
        "display_order": 2,
        "refresh_frequency": "daily"
    },
    "GASREGW": {
        "display_name": "Gas Prices (Regular)",
        "description": "U.S. regular all formulations retail gasoline prices",
        "source": "FRED",
        "unit": "$/Gallon",
        "weekday": 3,
        "display_order": 3,
        "refresh_frequency": "weekly"
    },
    "DHHNGSP": {
        "display_name": "Natural Gas Prices",
        "description": "Henry Hub natural gas spot price",
        "source": "FRED",
        "unit": "$/Million BTU",
        "weekday": 3,
        "display_order": 4,
        "refresh_frequency": "daily"
    },
    "CAUR": {
        "display_name": "California Unemployment Rate",
        "description": "Unemployment rate in California",
        "source": "FRED",
        "unit": "%",
        "weekday": 3,
        "display_order": 5,
        "refresh_frequency": "monthly"
    },
    "TXUR": {
        "display_name": "Texas Unemployment Rate",
        "description": "Unemployment rate in Texas",
        "source": "FRED",
        "unit": "%",
        "weekday": 3,
        "display_order": 6,
        "refresh_frequency": "monthly"
    },
    "NYUR": {
        "display_name": "New York Unemployment Rate",
        "description": "Unemployment rate in New York",
        "source": "FRED",
        "unit": "%",
        "weekday": 3,
        "display_order": 7,
        "refresh_frequency": "monthly"
    },

    # ========== FRIDAY: Markets & Week Summary ==========
    "SP500": {
        "display_name": "S&P 500 Index",
        "description": "S&P 500 stock market index",
        "source": "FRED",
        "unit": "Index",
        "weekday": 4,
        "display_order": 1,
        "refresh_frequency": "daily"
    },
    "DEXUSEU": {
        "display_name": "Dollar vs Euro Exchange Rate",
        "description": "U.S. dollars to one euro",
        "source": "FRED",
        "unit": "USD/EUR",
        "weekday": 4,
        "display_order": 2,
        "refresh_frequency": "daily"
    },
    "DEXCHUS": {
        "display_name": "Dollar vs Yuan Exchange Rate",
        "description": "Chinese yuan to one U.S. dollar",
        "source": "FRED",
        "unit": "CNY/USD",
        "weekday": 4,
        "display_order": 3,
        "refresh_frequency": "daily"
    },
    "DTWEXBGS": {
        "display_name": "Trade Weighted Dollar Index",
        "description": "Trade weighted U.S. dollar index: broad, goods and services",
        "source": "FRED",
        "unit": "Index",
        "weekday": 4,
        "display_order": 4,
        "refresh_frequency": "daily"
    },
    "VIXCLS": {
        "display_name": "VIX Volatility Index",
        "description": "CBOE volatility index (market fear gauge)",
        "source": "FRED",
        "unit": "Index",
        "weekday": 4,
        "display_order": 5,
        "refresh_frequency": "daily"
    },
    "BAMLH0A0HYM2": {
        "display_name": "High Yield Bond Spread",
        "description": "ICE BofA US High Yield Index Option-Adjusted Spread",
        "source": "FRED",
        "unit": "%",
        "weekday": 4,
        "display_order": 6,
        "refresh_frequency": "daily"
    },
    "T10YIE": {
        "display_name": "10-Year Breakeven Inflation Rate",
        "description": "10-year breakeven inflation rate (market inflation expectations)",
        "source": "FRED",
        "unit": "%",
        "weekday": 4,
        "display_order": 7,
        "refresh_frequency": "daily"
    },
}


def get_metrics_for_weekday(weekday: int) -> List[Dict]:
    """
    Get metrics configured for a specific weekday.

    Args:
        weekday: Day of week (0=Monday, 6=Sunday)

    Returns:
        List of metric configurations for that weekday
    """
    metrics = []
    for code, config in METRICS_CONFIG.items():
        if config.get("weekday") == weekday:
            metrics.append({
                "code": code,
                **config
            })

    # Sort by display_order
    metrics.sort(key=lambda x: x.get("display_order", 999))

    return metrics


def get_all_metric_codes() -> List[str]:
    """
    Get list of all metric codes.

    Returns:
        List of all metric codes
    """
    return list(METRICS_CONFIG.keys())


def get_metric_config(code: str) -> Dict:
    """
    Get configuration for a specific metric.

    Args:
        code: Metric code

    Returns:
        Metric configuration dict
    """
    return METRICS_CONFIG.get(code, {})
