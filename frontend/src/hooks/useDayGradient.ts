import { useMemo } from 'react'

export type DayGradient = {
  name: string
  from: string
  via?: string
  to: string
  description: string
}

const GRADIENTS: Record<number, DayGradient> = {
  1: {
    // Monday - Blue gradient (Federal/official)
    name: 'Federal Blue',
    from: 'from-blue-600/10',
    via: 'via-blue-500/5',
    to: 'to-background',
    description: 'Official federal data focus',
  },
  2: {
    // Tuesday - Green gradient (money/real estate)
    name: 'Market Green',
    from: 'from-green-600/10',
    via: 'via-emerald-500/5',
    to: 'to-background',
    description: 'Real estate and market data',
  },
  3: {
    // Wednesday - Purple gradient (data/analytics)
    name: 'Analytics Purple',
    from: 'from-purple-600/10',
    via: 'via-violet-500/5',
    to: 'to-background',
    description: 'Deep data analytics',
  },
  4: {
    // Thursday - Orange gradient (regional/warm)
    name: 'Regional Orange',
    from: 'from-orange-600/10',
    via: 'via-amber-500/5',
    to: 'to-background',
    description: 'Regional economic insights',
  },
  5: {
    // Friday - Teal gradient (summary/ocean)
    name: 'Summary Teal',
    from: 'from-teal-600/10',
    via: 'via-cyan-500/5',
    to: 'to-background',
    description: 'Weekly summary focus',
  },
  6: {
    // Saturday - Mixed gradient (weekend)
    name: 'Weekend Indigo',
    from: 'from-indigo-600/10',
    via: 'via-blue-500/5',
    to: 'to-background',
    description: 'Weekend market overview',
  },
  0: {
    // Sunday - Mixed gradient (weekend)
    name: 'Weekend Rose',
    from: 'from-rose-600/10',
    via: 'via-pink-500/5',
    to: 'to-background',
    description: 'Weekend planning',
  },
}

const ACCENT_COLORS: Record<number, string> = {
  1: 'hsl(217 91% 60%)', // blue
  2: 'hsl(142 76% 45%)', // green
  3: 'hsl(263 70% 60%)', // purple
  4: 'hsl(25 95% 55%)', // orange
  5: 'hsl(173 80% 40%)', // teal
  6: 'hsl(239 84% 67%)', // indigo
  0: 'hsl(350 89% 60%)', // rose
}

export function useDayGradient() {
  const gradient = useMemo(() => {
    const day = new Date().getDay()
    return GRADIENTS[day]
  }, [])

  const accentColor = useMemo(() => {
    const day = new Date().getDay()
    return ACCENT_COLORS[day]
  }, [])

  const gradientClass = useMemo(() => {
    return `bg-gradient-to-b ${gradient.from} ${gradient.via} ${gradient.to}`
  }, [gradient])

  return {
    gradient,
    accentColor,
    gradientClass,
  }
}
