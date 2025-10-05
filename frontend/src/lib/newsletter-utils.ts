/**
 * Utility functions for newsletter components
 *
 * Shared utilities for formatting, styling, and processing newsletter data
 */

import type { MetricType } from '@/types/newsletter'
import {
  TrendingUp,
  DollarSign,
  Building,
  BadgeDollarSign,
  Percent,
} from 'lucide-react'

/**
 * Badge color variants for different newsletter categories
 */
type BadgeVariant = 'blue' | 'green' | 'purple' | 'orange' | 'pink' | 'yellow' | 'indigo' | 'gray'

/**
 * Map newsletter categories to badge color variants
 *
 * @param category - Newsletter category string
 * @returns Badge variant for styling
 */
export function getCategoryColor(category: string): BadgeVariant {
  const categoryLower = category.toLowerCase()

  if (categoryLower.includes('houston')) return 'blue'
  if (categoryLower.includes('austin') || categoryLower.includes('san antonio')) return 'green'
  if (categoryLower.includes('national')) return 'purple'
  if (categoryLower.includes('capital markets')) return 'orange'
  if (categoryLower.includes('multifamily')) return 'pink'
  if (categoryLower.includes('retail')) return 'yellow'
  if (categoryLower.includes('student housing')) return 'indigo'

  return 'gray'
}

/**
 * Get icon component for a metric type
 *
 * @param type - Metric type
 * @returns Lucide icon component
 */
export function getMetricIcon(type: MetricType) {
  switch (type) {
    case 'cap_rate':
      return TrendingUp
    case 'deal_value':
      return DollarSign
    case 'square_footage':
      return Building
    case 'price_per_sf':
      return BadgeDollarSign
    case 'occupancy_rate':
      return Percent
  }
}

/**
 * Format metric type for display
 *
 * @param type - Metric type
 * @returns Human-readable metric type label
 */
export function formatMetricType(type: MetricType): string {
  const typeMap: Record<MetricType, string> = {
    cap_rate: 'Cap Rate',
    deal_value: 'Deal Value',
    square_footage: 'Square Footage',
    price_per_sf: 'Price/SF',
    occupancy_rate: 'Occupancy'
  }
  return typeMap[type]
}

/**
 * Format date as relative time string
 *
 * @param dateString - ISO date string
 * @returns Relative time string (e.g., "2 hours ago", "3 days ago")
 */
export function getRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)
  const diffWeeks = Math.floor(diffDays / 7)
  const diffMonths = Math.floor(diffDays / 30)

  if (diffSeconds < 60) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffWeeks < 4) return `${diffWeeks}w ago`
  if (diffMonths < 12) return `${diffMonths}mo ago`

  return date.toLocaleDateString()
}

/**
 * Format date for display with options
 *
 * @param dateString - ISO date string
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted date string
 */
export function formatDate(
  dateString: string,
  options?: Intl.DateTimeFormatOptions
): string {
  const date = new Date(dateString)
  const defaultOptions: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }

  return date.toLocaleString('en-US', options || defaultOptions)
}

/**
 * Truncate text to a maximum length with ellipsis
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + '...'
}

/**
 * Extract domain from email address
 *
 * @param email - Email address
 * @returns Domain portion of email
 */
export function getEmailDomain(email: string): string {
  const match = email.match(/@(.+)$/)
  return match ? match[1] : email
}

/**
 * Check if a URL is valid
 *
 * @param url - URL string to validate
 * @returns True if URL is valid
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Get color class for badge based on variant
 * This is used when you need the raw color class instead of variant prop
 *
 * @param variant - Badge variant
 * @returns Tailwind color classes
 */
export function getBadgeColorClass(variant: BadgeVariant): string {
  const colorMap: Record<BadgeVariant, string> = {
    blue: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    green: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    purple: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    orange: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    pink: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    indigo: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    gray: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  }
  return colorMap[variant]
}
