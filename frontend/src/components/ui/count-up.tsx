import { useEffect, useRef } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

interface CountUpProps {
  value: number
  className?: string
  decimals?: number
  duration?: number
  prefix?: string
  suffix?: string
}

export function CountUp({
  value,
  className = '',
  decimals = 0,
  duration = 1,
  prefix = '',
  suffix = '',
}: CountUpProps) {
  const springValue = useSpring(0, {
    duration: duration * 1000,
    bounce: 0,
  })

  const display = useTransform(springValue, (latest) => {
    return `${prefix}${latest.toFixed(decimals)}${suffix}`
  })

  const prevValueRef = useRef(value)

  useEffect(() => {
    if (prevValueRef.current !== value) {
      springValue.set(value)
      prevValueRef.current = value
    }
  }, [value, springValue])

  return <motion.span className={className}>{display}</motion.span>
}

interface AnimatedNumberProps {
  value: number
  className?: string
  formatValue?: (val: number) => string
}

export function AnimatedNumber({ value, className = '', formatValue }: AnimatedNumberProps) {
  const isFirstRender = useRef(true)

  const springValue = useSpring(value, {
    duration: 1000,
    bounce: 0,
  })

  const display = useTransform(springValue, (latest) => {
    if (formatValue) {
      return formatValue(latest)
    }
    return latest.toFixed(0)
  })

  useEffect(() => {
    if (isFirstRender.current) {
      // On first render, set immediately without animation
      springValue.set(value)
      isFirstRender.current = false
    } else {
      // On subsequent updates, animate
      springValue.set(value)
    }
  }, [value, springValue])

  return <motion.span className={className}>{display}</motion.span>
}
