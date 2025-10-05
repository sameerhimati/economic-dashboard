import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

interface ProgressBarProps {
  isLoading: boolean
}

export function ProgressBar({ isLoading }: ProgressBarProps) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (isLoading) {
      setProgress(0)
      // Simulate progress
      const intervals = [
        setTimeout(() => setProgress(30), 100),
        setTimeout(() => setProgress(60), 300),
        setTimeout(() => setProgress(80), 600),
      ]

      return () => intervals.forEach(clearTimeout)
    } else {
      // Complete the progress
      setProgress(100)
      // Reset after animation
      const timeout = setTimeout(() => setProgress(0), 500)
      return () => clearTimeout(timeout)
    }
  }, [isLoading])

  return (
    <AnimatePresence>
      {(isLoading || progress === 100) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-50 h-1"
        >
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{
              duration: progress === 100 ? 0.2 : 0.3,
              ease: 'easeOut',
            }}
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 shadow-lg shadow-blue-500/50"
          />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
