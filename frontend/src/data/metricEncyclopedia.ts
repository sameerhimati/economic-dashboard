/**
 * Comprehensive Metric Encyclopedia
 * Educational content for all economic indicators
 */

export interface MetricEducation {
  whatIsIt: string
  whyItMatters: string[]
  readingTheNumbers: {
    low: { range: string; meaning: string }
    normal: { range: string; meaning: string }
    high: { range: string; meaning: string }
  }
  whatToWatch: string[]
  keyThresholds: { value: string; meaning: string }[]
  historicalEvents: { year: string; event: string; impact: string }[]
  relatedMetrics: { code: string; name: string; relationship: string }[]
}

export const metricEncyclopedia: Record<string, MetricEducation> = {
  FEDFUNDS: {
    whatIsIt:
      "The interest rate that banks charge each other for overnight loans. Set by the Federal Reserve, it's the primary tool for controlling the economy.",
    whyItMatters: [
      "Controls the cost of borrowing across the entire economy",
      "Higher rates slow inflation but can slow growth",
      "Lower rates stimulate spending but can increase inflation",
      "Affects mortgage rates, credit cards, business loans, and savings accounts",
    ],
    readingTheNumbers: {
      low: { range: "0-1%", meaning: "Emergency stimulus - Fed fighting recession or crisis" },
      normal: { range: "2-4%", meaning: "Healthy economy with stable inflation" },
      high: { range: "5%+", meaning: "Fed aggressively fighting inflation" },
    },
    whatToWatch: [
      "Rising trend → Fed fighting inflation, borrowing costs increasing",
      "Falling trend → Fed stimulating growth, easier credit",
      "Sudden changes → Major policy shifts or economic emergencies",
      "Gap vs inflation rate → Shows Fed's stance (restrictive vs accommodative)",
    ],
    keyThresholds: [
      { value: "0-0.25%", meaning: "Zero lower bound - emergency lows" },
      { value: "2.5%", meaning: "Neutral rate - neither stimulating nor restricting" },
      { value: "5%+", meaning: "Restrictive territory - actively cooling economy" },
    ],
    historicalEvents: [
      { year: "2008", event: "Financial Crisis", impact: "Fed Funds cut to 0.25% from 5.25%" },
      { year: "1980", event: "Volcker Fighting Inflation", impact: "Peaked at 20% to break inflation spiral" },
      { year: "2020", event: "COVID-19 Pandemic", impact: "Emergency cut to near-zero in weeks" },
      { year: "2022-2023", event: "Post-COVID Inflation", impact: "Fastest rate hikes in 40 years to 5.5%" },
    ],
    relatedMetrics: [
      { code: "MORTGAGE30US", name: "30-Year Mortgage", relationship: "Mortgage rates track Fed Funds closely" },
      { code: "DGS10", name: "10-Year Treasury", relationship: "Long-term rates reflect Fed expectations" },
      { code: "CPIAUCSL", name: "Inflation (CPI)", relationship: "Fed's primary target for rate decisions" },
    ],
  },

  DFF: {
    whatIsIt:
      "The daily effective federal funds rate - the actual weighted average rate that banks charge each other for overnight loans.",
    whyItMatters: [
      "Shows the real-time cost of money in the banking system",
      "More volatile than the Fed's target rate",
      "Reflects actual market conditions vs Fed targets",
      "First signal of stress in the banking system",
    ],
    readingTheNumbers: {
      low: { range: "0-1%", meaning: "Emergency liquidity or crisis conditions" },
      normal: { range: "2-4%", meaning: "Normal banking operations" },
      high: { range: "5%+", meaning: "Tight liquidity or aggressive Fed policy" },
    },
    whatToWatch: [
      "Divergence from Fed target → Banking stress or excess liquidity",
      "Spikes above target → Banks scrambling for cash",
      "Below target → Excess reserves in system",
    ],
    keyThresholds: [
      { value: "Within 0.10% of target", meaning: "Normal market functioning" },
      { value: "+0.25% above target", meaning: "Potential liquidity stress" },
    ],
    historicalEvents: [
      { year: "2008", event: "Lehman Collapse", impact: "Rate spiked as banks stopped lending" },
      { year: "2020", event: "COVID Market Freeze", impact: "Fed flooded system with liquidity" },
    ],
    relatedMetrics: [
      { code: "FEDFUNDS", name: "Fed Funds Target", relationship: "DFF should track this closely" },
      { code: "SOFR", name: "SOFR Rate", relationship: "Alternative overnight lending rate" },
    ],
  },

  DFEDTARU: {
    whatIsIt:
      "The upper limit of the Federal Reserve's target range for the federal funds rate. The Fed sets a range (e.g., 5.25-5.50%), and this is the top.",
    whyItMatters: [
      "Shows the maximum rate the Fed wants banks to pay",
      "Part of the Fed's communication strategy",
      "Changes signal Fed policy shifts",
    ],
    readingTheNumbers: {
      low: { range: "0-1%", meaning: "Maximum stimulus" },
      normal: { range: "2-4%", meaning: "Normal policy stance" },
      high: { range: "5%+", meaning: "Fighting inflation aggressively" },
    },
    whatToWatch: [
      "Changes indicate Fed policy shifts",
      "Rising → Tightening monetary policy",
      "Falling → Loosening monetary policy",
    ],
    keyThresholds: [
      { value: "0.25%", meaning: "Zero lower bound" },
      { value: "5%+", meaning: "Restrictive policy" },
    ],
    historicalEvents: [
      { year: "2022-2023", event: "Inflation Fight", impact: "Raised from 0.25% to 5.50% in 18 months" },
    ],
    relatedMetrics: [
      { code: "FEDFUNDS", name: "Fed Funds Rate", relationship: "Midpoint of the range" },
    ],
  },

  DGS10: {
    whatIsIt:
      "The yield on 10-year U.S. Treasury bonds - essentially the interest rate the government pays to borrow for 10 years.",
    whyItMatters: [
      "Benchmark for mortgage rates and corporate borrowing",
      "Reflects market expectations for growth and inflation",
      "Flight to safety indicator during crises",
      "Influences stock valuations and investment decisions",
    ],
    readingTheNumbers: {
      low: { range: "0-2%", meaning: "Economic pessimism or crisis" },
      normal: { range: "2-4%", meaning: "Healthy growth expectations" },
      high: { range: "4%+", meaning: "High inflation fears or strong growth" },
    },
    whatToWatch: [
      "Rising → Higher borrowing costs, inflation concerns",
      "Falling → Economic slowdown fears, flight to safety",
      "Vs 2-year → Yield curve inversion predicts recessions",
    ],
    keyThresholds: [
      { value: "Below 1%", meaning: "Crisis or deflation fears" },
      { value: "3%", meaning: "Historical average" },
      { value: "Above 5%", meaning: "Serious inflation concerns" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Panic", impact: "Dropped to 0.5% as investors fled to safety" },
      { year: "1981", event: "Volcker Era", impact: "Peaked above 15% during inflation fight" },
      { year: "2022", event: "Inflation Surge", impact: "Rose from 1% to 4.5% in one year" },
    ],
    relatedMetrics: [
      { code: "DGS2", name: "2-Year Treasury", relationship: "Compare for yield curve" },
      { code: "MORTGAGE30US", name: "Mortgage Rates", relationship: "Mortgages track 10-year closely" },
      { code: "T10Y2Y", name: "Yield Curve", relationship: "Spread between 10Y and 2Y" },
    ],
  },

  DGS2: {
    whatIsIt:
      "The yield on 2-year U.S. Treasury bonds - the interest rate for shorter-term government borrowing.",
    whyItMatters: [
      "More sensitive to Fed policy than long-term rates",
      "Reflects near-term economic expectations",
      "Key component of yield curve analysis",
    ],
    readingTheNumbers: {
      low: { range: "0-1%", meaning: "Expecting Fed cuts or recession" },
      normal: { range: "2-3%", meaning: "Stable near-term outlook" },
      high: { range: "4%+", meaning: "Expecting high Fed rates" },
    },
    whatToWatch: [
      "Vs Fed Funds → Shows market expectations for Fed policy",
      "Vs 10-year → Yield curve inversion signals recession",
      "Rapid changes → Shifting Fed expectations",
    ],
    keyThresholds: [
      { value: "Above 10-year", meaning: "Inverted yield curve - recession warning" },
      { value: "Above Fed Funds", meaning: "Market expects rate hikes" },
    ],
    historicalEvents: [
      { year: "2022", event: "Yield Curve Inversion", impact: "2Y exceeded 10Y, predicting 2023 recession fears" },
    ],
    relatedMetrics: [
      { code: "DGS10", name: "10-Year Treasury", relationship: "Compare for yield curve slope" },
      { code: "FEDFUNDS", name: "Fed Funds Rate", relationship: "2Y tracks Fed expectations" },
    ],
  },

  T10Y2Y: {
    whatIsIt:
      "The difference between 10-year and 2-year Treasury yields. When negative (inverted), it has predicted every recession since 1955.",
    whyItMatters: [
      "Most reliable recession predictor in modern history",
      "Reflects market pessimism about long-term growth",
      "Shows tension between Fed policy and growth expectations",
    ],
    readingTheNumbers: {
      low: { range: "Negative", meaning: "Inverted - recession likely within 6-18 months" },
      normal: { range: "0-2%", meaning: "Healthy yield curve" },
      high: { range: "2%+", meaning: "Strong growth expectations" },
    },
    whatToWatch: [
      "Turning negative → Recession warning signal",
      "Steepening → Economic recovery expectations",
      "Flattening → Growth concerns increasing",
    ],
    keyThresholds: [
      { value: "Below 0%", meaning: "Inverted - recession warning" },
      { value: "0-0.5%", meaning: "Flattening - caution zone" },
      { value: "1%+", meaning: "Normal positive slope" },
    ],
    historicalEvents: [
      { year: "2006", event: "Pre-Financial Crisis", impact: "Inverted before 2008 crash" },
      { year: "2019", event: "Pre-COVID", impact: "Briefly inverted, then COVID recession hit" },
      { year: "2022", event: "Inflation Fight", impact: "Deeply inverted as Fed hiked aggressively" },
    ],
    relatedMetrics: [
      { code: "DGS10", name: "10-Year Treasury", relationship: "Numerator of the spread" },
      { code: "DGS2", name: "2-Year Treasury", relationship: "Denominator of the spread" },
      { code: "UNRATE", name: "Unemployment", relationship: "Rises after inversions" },
    ],
  },

  SOFR: {
    whatIsIt:
      "Secured Overnight Financing Rate - a measure of overnight lending secured by Treasury bonds. Replacing LIBOR as the benchmark rate.",
    whyItMatters: [
      "New standard for pricing trillions in loans and derivatives",
      "More transparent than the old LIBOR system",
      "Reflects actual Treasury repo market transactions",
    ],
    readingTheNumbers: {
      low: { range: "0-1%", meaning: "Low short-term rates" },
      normal: { range: "2-4%", meaning: "Normal money market conditions" },
      high: { range: "5%+", meaning: "Tight overnight funding" },
    },
    whatToWatch: [
      "Vs Fed Funds → Should track closely",
      "Spikes → Funding stress in repo market",
      "Used for pricing adjustable-rate mortgages and corporate loans",
    ],
    keyThresholds: [
      { value: "Within 0.10% of Fed Funds", meaning: "Normal market" },
      { value: "+0.25%", meaning: "Potential repo market stress" },
    ],
    historicalEvents: [
      { year: "2019", event: "Repo Market Seizure", impact: "Overnight rates spiked to 10%, Fed intervened" },
      { year: "2023", event: "LIBOR Sunset", impact: "SOFR became primary benchmark" },
    ],
    relatedMetrics: [
      { code: "FEDFUNDS", name: "Fed Funds Rate", relationship: "Should track closely" },
      { code: "DFF", name: "Daily Fed Funds", relationship: "Alternative overnight rate" },
    ],
  },

  MORTGAGE30US: {
    whatIsIt:
      "The average interest rate for a 30-year fixed-rate mortgage in the United States.",
    whyItMatters: [
      "Determines affordability for homebuyers",
      "Major driver of housing demand and home sales",
      "Impacts refinancing activity and consumer spending",
      "Each 1% increase reduces buying power by ~10%",
    ],
    readingTheNumbers: {
      low: { range: "Below 4%", meaning: "Very affordable - strong housing demand" },
      normal: { range: "4-6%", meaning: "Moderate housing activity" },
      high: { range: "7%+", meaning: "Expensive - housing market cooling" },
    },
    whatToWatch: [
      "Rising → Home sales fall, refinancing stops, prices may drop",
      "Falling → Buying surge, refinancing boom, price increases",
      "Vs 10-year Treasury → Typically 1.5-2% above",
    ],
    keyThresholds: [
      { value: "3%", meaning: "Historic lows - refinancing boom" },
      { value: "6%", meaning: "Long-term average" },
      { value: "7%+", meaning: "Housing market headwind" },
    ],
    historicalEvents: [
      { year: "2020-2021", event: "COVID Rate Cuts", impact: "Dropped to 2.65% - housing boom" },
      { year: "1981", event: "Volcker Era", impact: "Peaked at 18.45% - housing freeze" },
      { year: "2022-2023", event: "Inflation Fight", impact: "Jumped from 3% to 7.8% in 18 months" },
    ],
    relatedMetrics: [
      { code: "DGS10", name: "10-Year Treasury", relationship: "Mortgages track 10Y plus spread" },
      { code: "HOUST", name: "Housing Starts", relationship: "Falls when rates rise" },
      { code: "CSUSHPINSA", name: "Home Prices", relationship: "Higher rates slow price growth" },
    ],
  },

  MORTGAGE15US: {
    whatIsIt:
      "The average interest rate for a 15-year fixed-rate mortgage. Lower rate but higher monthly payment than 30-year.",
    whyItMatters: [
      "Popular for refinancing and second-home purchases",
      "Saves significant interest vs 30-year",
      "Indicator of refinancing activity",
    ],
    readingTheNumbers: {
      low: { range: "Below 3%", meaning: "Refinancing surge likely" },
      normal: { range: "3-5%", meaning: "Moderate activity" },
      high: { range: "6%+", meaning: "Refinancing stops" },
    },
    whatToWatch: [
      "Spread vs 30-year → Typically 0.5-0.75% lower",
      "Rising → Refinancing slows dramatically",
    ],
    keyThresholds: [
      { value: "2.5%", meaning: "Historic lows" },
      { value: "5%", meaning: "Long-term average" },
    ],
    historicalEvents: [
      { year: "2020-2021", event: "Refi Boom", impact: "Dropped to 2.1% - record refinancing" },
    ],
    relatedMetrics: [
      { code: "MORTGAGE30US", name: "30-Year Mortgage", relationship: "Typically 0.5-0.75% lower" },
    ],
  },

  HOUST: {
    whatIsIt:
      "Housing Starts - the number of new residential construction projects begun each month (in thousands, annual rate).",
    whyItMatters: [
      "Leading indicator for economic growth",
      "Creates construction jobs and economic activity",
      "Drives demand for building materials, appliances, furniture",
      "Reflects builder confidence in demand",
    ],
    readingTheNumbers: {
      low: { range: "Below 1,000K", meaning: "Housing recession or crisis" },
      normal: { range: "1,200-1,500K", meaning: "Healthy construction activity" },
      high: { range: "Above 1,600K", meaning: "Housing boom" },
    },
    whatToWatch: [
      "Rising → Economic optimism, job growth, material demand",
      "Falling → Builder pessimism, usually predicts slowdown",
      "Vs permits → Starts should follow permits",
    ],
    keyThresholds: [
      { value: "500K", meaning: "Crisis levels (2008 financial crisis)" },
      { value: "1,500K", meaning: "Long-term average" },
      { value: "2,000K+", meaning: "Boom levels (2005 peak)" },
    ],
    historicalEvents: [
      { year: "2008-2011", event: "Housing Crash", impact: "Collapsed from 2M to 500K" },
      { year: "2020-2021", event: "COVID Boom", impact: "Surged on low rates and remote work" },
      { year: "2022-2023", event: "Rate Shock", impact: "Fell 30% as mortgage rates doubled" },
    ],
    relatedMetrics: [
      { code: "PERMIT", name: "Building Permits", relationship: "Leading indicator for starts" },
      { code: "MORTGAGE30US", name: "Mortgage Rates", relationship: "Inverse - high rates kill starts" },
    ],
  },

  PERMIT: {
    whatIsIt:
      "Building Permits - the number of permits issued for new residential construction. Leading indicator that precedes actual construction.",
    whyItMatters: [
      "Predicts future housing starts by 1-2 months",
      "Shows builder confidence in future demand",
      "Early signal of housing market direction",
    ],
    readingTheNumbers: {
      low: { range: "Below 1,000K", meaning: "Builders pessimistic" },
      normal: { range: "1,200-1,500K", meaning: "Steady construction pipeline" },
      high: { range: "Above 1,600K", meaning: "Strong builder confidence" },
    },
    whatToWatch: [
      "Leading indicator → Predicts starts",
      "Rising → Bullish on housing demand",
      "Falling → Builder caution, expect lower starts",
    ],
    keyThresholds: [
      { value: "1,500K", meaning: "Healthy construction pipeline" },
    ],
    historicalEvents: [
      { year: "2008", event: "Housing Crash", impact: "Permits collapsed 75%" },
    ],
    relatedMetrics: [
      { code: "HOUST", name: "Housing Starts", relationship: "Permits lead starts by 1-2 months" },
    ],
  },

  UMCSENT: {
    whatIsIt:
      "University of Michigan Consumer Sentiment Index - a survey measuring consumer confidence and spending intentions.",
    whyItMatters: [
      "Consumer spending is 70% of GDP",
      "Predicts retail sales and economic growth",
      "Reflects inflation expectations",
    ],
    readingTheNumbers: {
      low: { range: "Below 70", meaning: "Consumer pessimism - recession risk" },
      normal: { range: "80-100", meaning: "Moderate confidence" },
      high: { range: "Above 100", meaning: "Strong optimism - spending likely" },
    },
    whatToWatch: [
      "Falling → Consumers cutting back, recession risk",
      "Rising → Spending surge likely",
      "Inflation expectations component → Fed watches closely",
    ],
    keyThresholds: [
      { value: "50", meaning: "Extreme pessimism (2008 crisis level)" },
      { value: "85", meaning: "Long-term average" },
      { value: "100+", meaning: "Strong confidence" },
    ],
    historicalEvents: [
      { year: "2008", event: "Financial Crisis", impact: "Dropped to 55 - lowest on record" },
      { year: "2022", event: "Inflation Surge", impact: "Fell to 50 despite low unemployment" },
    ],
    relatedMetrics: [
      { code: "RSXFS", name: "Retail Sales", relationship: "High sentiment → higher sales" },
      { code: "CPIAUCSL", name: "Inflation", relationship: "High inflation crushes sentiment" },
    ],
  },

  CSUSHPINSA: {
    whatIsIt:
      "S&P/Case-Shiller U.S. National Home Price Index - measures changes in home prices nationwide.",
    whyItMatters: [
      "Tracks the largest asset for most Americans",
      "Wealth effect drives consumer spending",
      "Warning signal for housing bubbles",
    ],
    readingTheNumbers: {
      low: { range: "Declining", meaning: "Housing correction or crash" },
      normal: { range: "2-5% annual growth", meaning: "Healthy appreciation" },
      high: { range: "10%+ annual growth", meaning: "Bubble risk" },
    },
    whatToWatch: [
      "Rapid growth → Affordability crisis, bubble risk",
      "Declining → Negative wealth effect, spending falls",
      "Vs income growth → Affordability measure",
    ],
    keyThresholds: [
      { value: "Declining YoY", meaning: "Housing recession" },
      { value: "15%+ YoY", meaning: "Bubble territory" },
    ],
    historicalEvents: [
      { year: "2006", event: "Peak Before Crash", impact: "Prices fell 27% over next 5 years" },
      { year: "2020-2022", event: "COVID Boom", impact: "Prices up 40% in 2 years" },
    ],
    relatedMetrics: [
      { code: "MORTGAGE30US", name: "Mortgage Rates", relationship: "Inverse - high rates slow prices" },
      { code: "MSPUS", name: "Median Home Price", relationship: "Alternative price measure" },
    ],
  },

  MSPUS: {
    whatIsIt:
      "Median Sales Price of Houses Sold in the United States. The middle price point - half sell for more, half for less.",
    whyItMatters: [
      "Simpler measure than indexes",
      "Tracks actual transaction prices",
      "Affordability benchmark for buyers",
    ],
    readingTheNumbers: {
      low: { range: "Below $300K", meaning: "More affordable housing" },
      normal: { range: "$300-400K", meaning: "Historical range" },
      high: { range: "Above $400K", meaning: "Affordability crisis" },
    },
    whatToWatch: [
      "Vs median income → Affordability ratio",
      "Regional variation → Migration patterns",
    ],
    keyThresholds: [
      { value: "$200K", meaning: "Post-crisis lows (2011)" },
      { value: "$450K+", meaning: "Peak levels (2022)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Peak Prices", impact: "Hit $480K before rate shock" },
    ],
    relatedMetrics: [
      { code: "CSUSHPINSA", name: "Case-Shiller Index", relationship: "Alternative price measure" },
    ],
  },

  RRVRUSQ156N: {
    whatIsIt:
      "Rental Vacancy Rate - percentage of rental housing units that are vacant and available for rent.",
    whyItMatters: [
      "Indicates rental market tightness",
      "High vacancy → rents fall",
      "Low vacancy → rent surge",
    ],
    readingTheNumbers: {
      low: { range: "Below 6%", meaning: "Tight market - rising rents" },
      normal: { range: "6-8%", meaning: "Balanced market" },
      high: { range: "Above 9%", meaning: "Excess supply - falling rents" },
    },
    whatToWatch: [
      "Falling → Rents rising, housing shortage",
      "Rising → Overbuilding, rent pressure easing",
    ],
    keyThresholds: [
      { value: "5%", meaning: "Very tight - rapid rent growth" },
      { value: "10%+", meaning: "Oversupply" },
    ],
    historicalEvents: [
      { year: "2009", event: "Foreclosure Crisis", impact: "Vacancy spiked to 11%" },
    ],
    relatedMetrics: [
      { code: "HOUST", name: "Housing Starts", relationship: "High starts can increase vacancy" },
    ],
  },

  GDP: {
    whatIsIt:
      "Gross Domestic Product - the total value of all goods and services produced in the U.S. economy.",
    whyItMatters: [
      "Primary measure of economic health",
      "Growth above 2% considered healthy",
      "Negative growth for 2 quarters = technical recession",
    ],
    readingTheNumbers: {
      low: { range: "Below 0%", meaning: "Recession - economy shrinking" },
      normal: { range: "2-3%", meaning: "Healthy steady growth" },
      high: { range: "Above 4%", meaning: "Strong expansion - inflation risk" },
    },
    whatToWatch: [
      "Two negative quarters → Technical recession",
      "Components → Consumer, business, government, net exports",
      "Real vs nominal → Inflation-adjusted growth",
    ],
    keyThresholds: [
      { value: "0%", meaning: "Stagnation line" },
      { value: "2%", meaning: "Long-term trend growth" },
      { value: "4%+", meaning: "Overheating risk" },
    ],
    historicalEvents: [
      { year: "2008-2009", event: "Great Recession", impact: "GDP fell 4.3% - worst since WWII" },
      { year: "2020 Q2", event: "COVID Lockdowns", impact: "GDP fell 31% annualized - unprecedented" },
    ],
    relatedMetrics: [
      { code: "UNRATE", name: "Unemployment", relationship: "Inverse - GDP growth lowers unemployment" },
      { code: "RSXFS", name: "Retail Sales", relationship: "Consumer spending is 70% of GDP" },
    ],
  },

  UNRATE: {
    whatIsIt:
      "Unemployment Rate - percentage of the labor force that is jobless and actively seeking work.",
    whyItMatters: [
      "Key measure of labor market health",
      "Fed's dual mandate: low unemployment and stable prices",
      "Below 4% historically very low",
      "Lags economy - rises after recession starts",
    ],
    readingTheNumbers: {
      low: { range: "Below 4%", meaning: "Very tight labor market - wage pressure" },
      normal: { range: "4-5%", meaning: "Full employment" },
      high: { range: "Above 6%", meaning: "Economic weakness" },
    },
    whatToWatch: [
      "Rising → Recession signal, spending falls",
      "Falling → Growth, but can signal inflation pressure",
      "Vs job openings → Labor market tightness",
    ],
    keyThresholds: [
      { value: "3.5%", meaning: "50-year lows - extreme tightness" },
      { value: "5%", meaning: "Long-term average" },
      { value: "10%+", meaning: "Severe recession" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Lockdowns", impact: "Spiked to 14.7% in one month" },
      { year: "2009", event: "Financial Crisis Peak", impact: "Hit 10% - highest in decades" },
      { year: "2019-2020", event: "Pre-COVID", impact: "Fell to 3.5% - 50-year low" },
    ],
    relatedMetrics: [
      { code: "PAYEMS", name: "Nonfarm Payrolls", relationship: "Job growth lowers unemployment" },
      { code: "JTSJOL", name: "Job Openings", relationship: "High openings with low unemployment = tight market" },
    ],
  },

  PAYEMS: {
    whatIsIt:
      "Nonfarm Payrolls - total number of paid workers in the U.S. excluding farm workers, private household employees, and non-profit employees.",
    whyItMatters: [
      "Most watched monthly economic indicator",
      "Moves markets significantly on release day",
      "Leading indicator of consumer spending",
    ],
    readingTheNumbers: {
      low: { range: "Below 100K/month", meaning: "Weak job growth - recession risk" },
      normal: { range: "150-250K/month", meaning: "Steady healthy growth" },
      high: { range: "Above 300K/month", meaning: "Strong growth - inflation pressure" },
    },
    whatToWatch: [
      "Negative → Recession signal",
      "Consistently strong → Wage pressure, inflation risk",
      "Revisions → Previous months often revised significantly",
    ],
    keyThresholds: [
      { value: "0", meaning: "Breakeven - no job growth" },
      { value: "200K/month", meaning: "Healthy sustainable pace" },
      { value: "500K+/month", meaning: "Rapid recovery" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Crash", impact: "Lost 22M jobs in 2 months" },
      { year: "2021-2022", event: "Recovery", impact: "Added 400-500K/month" },
    ],
    relatedMetrics: [
      { code: "UNRATE", name: "Unemployment", relationship: "Inverse - job growth lowers unemployment" },
    ],
  },

  JTSJOL: {
    whatIsIt:
      "Job Openings and Labor Turnover Survey (JOLTS) - number of job openings in the U.S. economy.",
    whyItMatters: [
      "Measures labor demand vs supply",
      "High openings with low unemployment = worker shortage",
      "Fed watches for wage pressure signals",
    ],
    readingTheNumbers: {
      low: { range: "Below 6M", meaning: "Weak labor demand" },
      normal: { range: "6-8M", meaning: "Balanced labor market" },
      high: { range: "Above 10M", meaning: "Severe worker shortage" },
    },
    whatToWatch: [
      "Openings per unemployed → Labor market tightness",
      "Rising → Wage pressure, inflation risk",
      "Falling → Cooling labor market, recession risk",
    ],
    keyThresholds: [
      { value: "1:1 ratio with unemployed", meaning: "Balanced market" },
      { value: "2:1 ratio", meaning: "Extreme worker shortage (2022)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Post-COVID Shortage", impact: "11M openings - historic high" },
    ],
    relatedMetrics: [
      { code: "UNRATE", name: "Unemployment", relationship: "High openings + low unemployment = tight market" },
    ],
  },

  CPIAUCSL: {
    whatIsIt:
      "Consumer Price Index - measures the average change in prices paid by consumers for goods and services.",
    whyItMatters: [
      "Primary inflation measure",
      "Determines Social Security adjustments",
      "Fed targets 2% annual inflation",
      "Erodes purchasing power when high",
    ],
    readingTheNumbers: {
      low: { range: "Below 1%", meaning: "Deflation risk" },
      normal: { range: "2-3%", meaning: "Fed's comfort zone" },
      high: { range: "Above 5%", meaning: "High inflation - Fed fights it" },
    },
    whatToWatch: [
      "Rising → Fed will raise rates, borrowing costs up",
      "Falling → Easing price pressure, potential rate cuts",
      "Core vs headline → Excludes volatile food/energy",
    ],
    keyThresholds: [
      { value: "2%", meaning: "Fed's target" },
      { value: "5%+", meaning: "Requires aggressive Fed action" },
      { value: "10%+", meaning: "Crisis level (1970s/2022)" },
    ],
    historicalEvents: [
      { year: "1979-1980", event: "Volcker's Fight", impact: "Peaked at 14.8%" },
      { year: "2022", event: "Post-COVID", impact: "Hit 9.1% - 40-year high" },
    ],
    relatedMetrics: [
      { code: "PCEPI", name: "PCE Inflation", relationship: "Fed's preferred measure" },
      { code: "FEDFUNDS", name: "Fed Funds Rate", relationship: "Fed raises rates to fight CPI" },
    ],
  },

  PCEPI: {
    whatIsIt:
      "Personal Consumption Expenditures Price Index - the Federal Reserve's preferred inflation measure.",
    whyItMatters: [
      "Fed's official inflation target is 2% PCE",
      "Broader than CPI, includes more services",
      "Adjusts for consumer substitution",
    ],
    readingTheNumbers: {
      low: { range: "Below 1.5%", meaning: "Below Fed target" },
      normal: { range: "2-2.5%", meaning: "Fed's comfort zone" },
      high: { range: "Above 4%", meaning: "Fed will fight it" },
    },
    whatToWatch: [
      "Core PCE → Excludes food/energy volatility",
      "Fed's 2% target → Official mandate",
      "Typically 0.5% below CPI",
    ],
    keyThresholds: [
      { value: "2%", meaning: "Fed's explicit target" },
      { value: "4%+", meaning: "Well above target - aggressive action" },
    ],
    historicalEvents: [
      { year: "2022", event: "Inflation Surge", impact: "Hit 7% - highest since 1982" },
    ],
    relatedMetrics: [
      { code: "CPIAUCSL", name: "CPI Inflation", relationship: "Alternative inflation measure" },
      { code: "PCEPILFE", name: "Core PCE", relationship: "Excludes food/energy" },
    ],
  },

  PCEPILFE: {
    whatIsIt:
      "Core PCE Price Index - Personal Consumption Expenditures excluding food and energy prices.",
    whyItMatters: [
      "Removes volatile food/energy to see underlying inflation",
      "Fed watches this most closely",
      "Better predictor of future inflation",
    ],
    readingTheNumbers: {
      low: { range: "Below 1.5%", meaning: "Disinflationary pressure" },
      normal: { range: "2%", meaning: "Fed's sweet spot" },
      high: { range: "Above 3%", meaning: "Broad inflation pressure" },
    },
    whatToWatch: [
      "Most important for Fed decisions",
      "Services vs goods → Services inflation stickier",
      "Rising → Fed stays tight longer",
    ],
    keyThresholds: [
      { value: "2%", meaning: "Fed's target" },
      { value: "5%+", meaning: "Severe inflation (2022)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Inflation Peak", impact: "Hit 5.4% - highest in 40 years" },
    ],
    relatedMetrics: [
      { code: "PCEPI", name: "Headline PCE", relationship: "Adds food/energy volatility" },
    ],
  },

  RSXFS: {
    whatIsIt:
      "Retail Sales - total sales at retail and food service establishments. Early indicator of consumer spending.",
    whyItMatters: [
      "Consumer spending is 70% of GDP",
      "Leading indicator for economic growth",
      "Reflects consumer confidence in real-time",
    ],
    readingTheNumbers: {
      low: { range: "Below 0% MoM", meaning: "Consumer pullback - recession risk" },
      normal: { range: "0.3-0.6% MoM", meaning: "Steady spending growth" },
      high: { range: "Above 1% MoM", meaning: "Strong consumer demand" },
    },
    whatToWatch: [
      "Holiday season → Nov/Dec critical for retailers",
      "Excluding autos → Core spending trend",
      "Real vs nominal → Inflation-adjusted growth",
    ],
    keyThresholds: [
      { value: "0%", meaning: "Stagnant spending" },
      { value: "0.5%/month", meaning: "Healthy growth" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Lockdowns", impact: "Plunged 14.7% in one month" },
    ],
    relatedMetrics: [
      { code: "UMCSENT", name: "Consumer Sentiment", relationship: "Confidence drives spending" },
    ],
  },

  INDPRO: {
    whatIsIt:
      "Industrial Production Index - measures output of factories, mines, and utilities.",
    whyItMatters: [
      "Tracks manufacturing sector health",
      "Leading indicator for GDP",
      "Reflects business investment and demand",
    ],
    readingTheNumbers: {
      low: { range: "Declining", meaning: "Manufacturing recession" },
      normal: { range: "1-2% annual growth", meaning: "Steady factory output" },
      high: { range: "Above 3%", meaning: "Manufacturing boom" },
    },
    whatToWatch: [
      "Declining → Recession warning",
      "Capacity utilization → How much factories are used",
    ],
    keyThresholds: [
      { value: "Negative growth", meaning: "Manufacturing contraction" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Shutdown", impact: "Fell 16% in two months" },
    ],
    relatedMetrics: [
      { code: "TCU", name: "Capacity Utilization", relationship: "Measures factory usage rate" },
    ],
  },

  TCU: {
    whatIsIt:
      "Capacity Utilization - percentage of total industrial capacity currently in use.",
    whyItMatters: [
      "Shows slack in economy",
      "Above 80% signals inflation pressure",
      "Below 75% suggests weak demand",
    ],
    readingTheNumbers: {
      low: { range: "Below 75%", meaning: "Excess capacity - weak demand" },
      normal: { range: "75-80%", meaning: "Healthy utilization" },
      high: { range: "Above 82%", meaning: "Maxed out - inflation risk" },
    },
    whatToWatch: [
      "Above 80% → Inflation pressure builds",
      "Falling → Recession signal",
    ],
    keyThresholds: [
      { value: "70%", meaning: "Severe recession (2009)" },
      { value: "80%", meaning: "Inflation warning threshold" },
    ],
    historicalEvents: [
      { year: "2009", event: "Financial Crisis", impact: "Fell to 66% - record low" },
    ],
    relatedMetrics: [
      { code: "INDPRO", name: "Industrial Production", relationship: "Output level vs capacity" },
    ],
  },

  DCOILWTICO: {
    whatIsIt:
      "West Texas Intermediate (WTI) Crude Oil Price - the U.S. benchmark for oil prices.",
    whyItMatters: [
      "Drives gas prices and inflation",
      "Major input cost for transportation and manufacturing",
      "Geopolitical indicator",
    ],
    readingTheNumbers: {
      low: { range: "Below $50", meaning: "Cheap energy - deflationary pressure" },
      normal: { range: "$60-80", meaning: "Balanced market" },
      high: { range: "Above $100", meaning: "Energy shock - inflation spike" },
    },
    whatToWatch: [
      "Rapid rises → Gas prices up, inflation pressure",
      "Supply shocks → Wars, OPEC cuts, hurricanes",
      "Demand signals → Economic growth indicator",
    ],
    keyThresholds: [
      { value: "$30", meaning: "Crisis lows (2020 COVID)" },
      { value: "$100+", meaning: "Inflationary shock" },
      { value: "$147", meaning: "All-time high (2008)" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Crash", impact: "Briefly negative - no storage left" },
      { year: "2022", event: "Ukraine War", impact: "Spiked to $120 on supply fears" },
    ],
    relatedMetrics: [
      { code: "GASREGW", name: "Gas Prices", relationship: "Oil prices drive gas prices" },
      { code: "CPIAUCSL", name: "CPI Inflation", relationship: "Oil spikes increase CPI" },
    ],
  },

  DCOILBRENTEU: {
    whatIsIt:
      "Brent Crude Oil Price - the international benchmark for oil, sourced from the North Sea.",
    whyItMatters: [
      "Global oil price reference",
      "Typically $2-5 above WTI",
      "Reflects international supply/demand",
    ],
    readingTheNumbers: {
      low: { range: "Below $50", meaning: "Global demand weak" },
      normal: { range: "$60-80", meaning: "Balanced market" },
      high: { range: "Above $100", meaning: "Supply crisis or demand surge" },
    },
    whatToWatch: [
      "Vs WTI spread → Transport costs and regional demand",
      "OPEC decisions → Supply cuts/increases",
    ],
    keyThresholds: [
      { value: "$100+", meaning: "Inflationary shock globally" },
    ],
    historicalEvents: [
      { year: "2022", event: "Ukraine War", impact: "Europe scrambled for non-Russian oil" },
    ],
    relatedMetrics: [
      { code: "DCOILWTICO", name: "WTI Oil", relationship: "U.S. benchmark comparison" },
    ],
  },

  GASREGW: {
    whatIsIt:
      "U.S. Regular Gasoline Prices - national average retail price for a gallon of regular gas.",
    whyItMatters: [
      "Directly impacts consumer budgets",
      "Visible inflation indicator",
      "Political implications",
    ],
    readingTheNumbers: {
      low: { range: "Below $2.50", meaning: "Cheap gas - consumer relief" },
      normal: { range: "$2.50-3.50", meaning: "Moderate prices" },
      high: { range: "Above $4", meaning: "Consumer stress" },
    },
    whatToWatch: [
      "Rising → Inflation pressure, consumer spending squeeze",
      "Summer driving season → Seasonal demand spike",
    ],
    keyThresholds: [
      { value: "$4", meaning: "Psychological threshold - consumer pain" },
      { value: "$5+", meaning: "Crisis level (2022)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Ukraine War", impact: "Hit $5.02 - all-time high" },
    ],
    relatedMetrics: [
      { code: "DCOILWTICO", name: "Oil Prices", relationship: "Oil drives gas prices" },
    ],
  },

  DHHNGSP: {
    whatIsIt:
      "Henry Hub Natural Gas Spot Price - benchmark price for natural gas in the U.S.",
    whyItMatters: [
      "Heating costs for homes and businesses",
      "Power generation input",
      "Winter demand driver",
    ],
    readingTheNumbers: {
      low: { range: "Below $2", meaning: "Cheap heating/power" },
      normal: { range: "$2-4", meaning: "Moderate prices" },
      high: { range: "Above $6", meaning: "Energy crisis" },
    },
    whatToWatch: [
      "Winter → Heating demand spikes",
      "Europe crisis → U.S. LNG exports surge",
    ],
    keyThresholds: [
      { value: "$10+", meaning: "Crisis (2022 Europe energy shock)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Europe Energy Crisis", impact: "U.S. exports surged, prices spiked" },
    ],
    relatedMetrics: [
      { code: "DCOILWTICO", name: "Oil Prices", relationship: "Alternative energy source" },
    ],
  },

  CAUR: {
    whatIsIt:
      "California Unemployment Rate - jobless rate in the largest state economy.",
    whyItMatters: [
      "California is 15% of U.S. GDP",
      "Tech sector bellwether",
      "Trends often lead national patterns",
    ],
    readingTheNumbers: {
      low: { range: "Below 5%", meaning: "Strong California economy" },
      normal: { range: "5-7%", meaning: "Moderate conditions" },
      high: { range: "Above 8%", meaning: "California recession" },
    },
    whatToWatch: [
      "Tech sector layoffs → Leading indicator",
      "Vs national rate → Regional strength",
    ],
    keyThresholds: [
      { value: "4%", meaning: "Very tight labor market" },
      { value: "10%+", meaning: "Severe recession" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Lockdowns", impact: "Spiked to 16% - strict restrictions" },
    ],
    relatedMetrics: [
      { code: "UNRATE", name: "National Unemployment", relationship: "California vs U.S. comparison" },
    ],
  },

  TXUR: {
    whatIsIt:
      "Texas Unemployment Rate - jobless rate in the second-largest state economy.",
    whyItMatters: [
      "Energy sector indicator",
      "Business-friendly state trends",
      "Migration destination",
    ],
    readingTheNumbers: {
      low: { range: "Below 4%", meaning: "Strong Texas economy" },
      normal: { range: "4-6%", meaning: "Moderate conditions" },
      high: { range: "Above 7%", meaning: "Texas weakness" },
    },
    whatToWatch: [
      "Oil prices → Energy jobs impact",
      "Migration → People moving from high-tax states",
    ],
    keyThresholds: [
      { value: "3.5%", meaning: "Very tight - worker shortage" },
    ],
    historicalEvents: [
      { year: "2020", event: "Oil Crash + COVID", impact: "Dual shock to energy and services" },
    ],
    relatedMetrics: [
      { code: "DCOILWTICO", name: "Oil Prices", relationship: "Oil drives Texas energy jobs" },
    ],
  },

  NYUR: {
    whatIsIt:
      "New York Unemployment Rate - jobless rate in New York state.",
    whyItMatters: [
      "Financial sector bellwether",
      "NYC trends impact national finance",
      "High-cost labor market",
    ],
    readingTheNumbers: {
      low: { range: "Below 4%", meaning: "Strong NY economy" },
      normal: { range: "4-6%", meaning: "Moderate conditions" },
      high: { range: "Above 7%", meaning: "NY weakness" },
    },
    whatToWatch: [
      "Finance sector → Wall Street job trends",
      "NYC vs state → Urban/rural divide",
    ],
    keyThresholds: [
      { value: "4%", meaning: "Tight labor market" },
    ],
    historicalEvents: [
      { year: "2020", event: "COVID Lockdowns", impact: "Hit 16% - service sector collapse" },
    ],
    relatedMetrics: [
      { code: "UNRATE", name: "National Unemployment", relationship: "NY vs U.S. comparison" },
    ],
  },

  SP500: {
    whatIsIt:
      "S&P 500 Stock Market Index - tracks the 500 largest U.S. public companies.",
    whyItMatters: [
      "Wealth indicator for investors",
      "Business confidence signal",
      "Retirement account value",
      "Forward-looking economic indicator",
    ],
    readingTheNumbers: {
      low: { range: "Bear market (-20%)", meaning: "Recession fears or crisis" },
      normal: { range: "Steady growth", meaning: "Economic optimism" },
      high: { range: "All-time highs", meaning: "Strong confidence or bubble risk" },
    },
    whatToWatch: [
      "Volatility → Fear vs confidence",
      "Earnings reports → Corporate health",
      "Fed policy → Rate hikes hurt stocks",
    ],
    keyThresholds: [
      { value: "-20% from peak", meaning: "Bear market - recession likely" },
      { value: "+20% from low", meaning: "Bull market" },
    ],
    historicalEvents: [
      { year: "2008", event: "Financial Crisis", impact: "Fell 57% from peak" },
      { year: "2020", event: "COVID Crash", impact: "Fell 34% in weeks, then V-recovery" },
      { year: "2022", event: "Rate Hikes", impact: "Down 25% as Fed fought inflation" },
    ],
    relatedMetrics: [
      { code: "VIXCLS", name: "VIX Volatility", relationship: "Inverse - VIX spikes when S&P falls" },
      { code: "FEDFUNDS", name: "Fed Funds Rate", relationship: "Higher rates pressure stocks" },
    ],
  },

  DEXUSEU: {
    whatIsIt:
      "Dollar vs Euro Exchange Rate - how many U.S. dollars it takes to buy one euro.",
    whyItMatters: [
      "Trade competitiveness indicator",
      "Strong dollar hurts exports, helps imports",
      "Weak dollar helps exports, hurts imports",
    ],
    readingTheNumbers: {
      low: { range: "Below 1.05", meaning: "Very strong dollar vs euro" },
      normal: { range: "1.10-1.20", meaning: "Balanced exchange" },
      high: { range: "Above 1.25", meaning: "Weak dollar vs euro" },
    },
    whatToWatch: [
      "Fed vs ECB policy → Rate differentials drive FX",
      "Strong dollar → U.S. exports expensive",
    ],
    keyThresholds: [
      { value: "Parity (1.00)", meaning: "Equal value - rare, signals crisis" },
    ],
    historicalEvents: [
      { year: "2022", event: "Fed Rate Hikes", impact: "Dollar hit parity with euro - strongest in 20 years" },
    ],
    relatedMetrics: [
      { code: "DTWEXBGS", name: "Dollar Index", relationship: "Broad dollar strength measure" },
    ],
  },

  DEXCHUS: {
    whatIsIt:
      "Dollar vs Yuan Exchange Rate - how many Chinese yuan it takes to buy one U.S. dollar.",
    whyItMatters: [
      "Trade balance with China",
      "Manufacturing competitiveness",
      "Geopolitical indicator",
    ],
    readingTheNumbers: {
      low: { range: "Below 6.5", meaning: "Strong yuan vs dollar" },
      normal: { range: "6.5-7.0", meaning: "Balanced exchange" },
      high: { range: "Above 7.0", meaning: "Weak yuan vs dollar" },
    },
    whatToWatch: [
      "China controls yuan → Policy signal",
      "Above 7.0 → Psychological threshold",
    ],
    keyThresholds: [
      { value: "7.0", meaning: "Key psychological level" },
    ],
    historicalEvents: [
      { year: "2019", event: "Trade War", impact: "Broke 7.0 - escalation signal" },
    ],
    relatedMetrics: [
      { code: "DTWEXBGS", name: "Dollar Index", relationship: "Broad dollar strength" },
    ],
  },

  DTWEXBGS: {
    whatIsIt:
      "Trade Weighted Dollar Index - measures the dollar's value against a basket of foreign currencies weighted by trade volume.",
    whyItMatters: [
      "Overall dollar strength/weakness",
      "U.S. export competitiveness",
      "Inflation implications",
    ],
    readingTheNumbers: {
      low: { range: "Below 100", meaning: "Weak dollar - good for exports" },
      normal: { range: "100-115", meaning: "Moderate strength" },
      high: { range: "Above 120", meaning: "Very strong dollar - export headwind" },
    },
    whatToWatch: [
      "Rising → U.S. exports get expensive, imports cheap",
      "Fed policy → Rate hikes strengthen dollar",
    ],
    keyThresholds: [
      { value: "100", meaning: "Baseline level" },
      { value: "125+", meaning: "Extremely strong (2022-2023)" },
    ],
    historicalEvents: [
      { year: "2022", event: "Fed Hikes", impact: "Hit 128 - 20-year high" },
    ],
    relatedMetrics: [
      { code: "DEXUSEU", name: "Dollar vs Euro", relationship: "Component of the index" },
    ],
  },

  VIXCLS: {
    whatIsIt:
      "CBOE Volatility Index (VIX) - measures expected stock market volatility over the next 30 days. Known as the 'fear gauge.'",
    whyItMatters: [
      "Investor fear/confidence indicator",
      "Spikes during crises",
      "Used for hedging strategies",
    ],
    readingTheNumbers: {
      low: { range: "Below 15", meaning: "Market complacency - low fear" },
      normal: { range: "15-20", meaning: "Moderate volatility" },
      high: { range: "Above 30", meaning: "High fear - crisis or crash" },
    },
    whatToWatch: [
      "Spikes → Market crashes or crises",
      "Low VIX → Complacency risk",
      "Inverse to S&P 500 → Fear vs greed",
    ],
    keyThresholds: [
      { value: "12", meaning: "Extreme complacency" },
      { value: "30+", meaning: "High fear - major selloff" },
      { value: "80+", meaning: "Panic (2008, 2020)" },
    ],
    historicalEvents: [
      { year: "2008", event: "Lehman Collapse", impact: "Spiked to 80 - historic panic" },
      { year: "2020", event: "COVID Crash", impact: "Hit 82 - fastest spike ever" },
    ],
    relatedMetrics: [
      { code: "SP500", name: "S&P 500", relationship: "Inverse - VIX rises when stocks fall" },
    ],
  },

  BAMLH0A0HYM2: {
    whatIsIt:
      "High Yield Bond Spread - the extra yield investors demand to hold risky 'junk bonds' instead of safe Treasuries.",
    whyItMatters: [
      "Credit market stress indicator",
      "Corporate distress signal",
      "Recession predictor",
    ],
    readingTheNumbers: {
      low: { range: "Below 3%", meaning: "Low risk perception - complacency" },
      normal: { range: "3-5%", meaning: "Normal credit conditions" },
      high: { range: "Above 7%", meaning: "Credit stress - recession risk" },
    },
    whatToWatch: [
      "Widening → Investors fear defaults",
      "Narrowing → Risk appetite returning",
      "Above 10% → Crisis (2008, 2020)",
    ],
    keyThresholds: [
      { value: "3%", meaning: "Very tight - complacency" },
      { value: "10%+", meaning: "Crisis - credit frozen" },
    ],
    historicalEvents: [
      { year: "2008", event: "Financial Crisis", impact: "Spread hit 20% - credit freeze" },
      { year: "2020", event: "COVID Crash", impact: "Spiked to 11% before Fed intervention" },
    ],
    relatedMetrics: [
      { code: "SP500", name: "S&P 500", relationship: "Spread widens when stocks fall" },
    ],
  },

  T10YIE: {
    whatIsIt:
      "10-Year Breakeven Inflation Rate - the market's expectation for average inflation over the next 10 years, derived from Treasury vs TIPS yields.",
    whyItMatters: [
      "Market inflation expectations",
      "Fed credibility gauge",
      "Real interest rate indicator",
    ],
    readingTheNumbers: {
      low: { range: "Below 1.5%", meaning: "Deflation fears" },
      normal: { range: "2-2.5%", meaning: "Anchored at Fed target" },
      high: { range: "Above 3%", meaning: "Inflation concerns rising" },
    },
    whatToWatch: [
      "Above 2.5% → Inflation expectations unanchored",
      "Below 1.5% → Deflation or recession fears",
      "Fed watches closely → Credibility indicator",
    ],
    keyThresholds: [
      { value: "2%", meaning: "Fed's target - well-anchored" },
      { value: "3%+", meaning: "Inflation expectations rising" },
    ],
    historicalEvents: [
      { year: "2022", event: "Inflation Surge", impact: "Hit 3% - Fed credibility tested" },
    ],
    relatedMetrics: [
      { code: "CPIAUCSL", name: "CPI Inflation", relationship: "Actual vs expected inflation" },
      { code: "DGS10", name: "10-Year Treasury", relationship: "Component of calculation" },
    ],
  },
}

// Helper function to get metric education
export function getMetricEducation(code: string): MetricEducation | null {
  return metricEncyclopedia[code] || null
}

// Helper function to check if metric has education
export function hasMetricEducation(code: string): boolean {
  return code in metricEncyclopedia
}
