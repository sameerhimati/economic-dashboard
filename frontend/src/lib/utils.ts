import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date | undefined | null): string {
  if (!date) return 'Unknown date'
  try {
    const d = new Date(date)
    if (isNaN(d.getTime())) return 'Invalid date'
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return 'Invalid date'
  }
}

export function formatDateTime(date: string | Date | undefined | null): string {
  if (!date) return 'Unknown date'
  try {
    const d = new Date(date)
    if (isNaN(d.getTime())) return 'Invalid date'
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch {
    return 'Invalid date'
  }
}

export function formatNumber(num: number | undefined | null, decimals: number = 2): string {
  if (num === undefined || num === null || isNaN(num)) return '0.00'
  try {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  } catch {
    return '0.00'
  }
}

export function formatPercent(num: number | undefined | null, decimals: number = 2): string {
  if (num === undefined || num === null || isNaN(num)) return '+0.00%'
  try {
    return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`
  } catch {
    return '+0.00%'
  }
}

export function formatCurrency(num: number | undefined | null): string {
  if (num === undefined || num === null || isNaN(num)) return '$0.00'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num)
  } catch {
    return '$0.00'
  }
}
