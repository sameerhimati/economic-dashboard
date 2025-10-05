import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { X, ArrowRight, Star, RefreshCw, Keyboard } from 'lucide-react'
import { useSettings } from '@/hooks/useSettings'

interface TourStep {
  target?: string
  title: string
  description: string
  icon: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
}

const TOUR_STEPS: TourStep[] = [
  {
    title: 'Welcome to Your Economic Dashboard',
    description:
      "Get instant insights into economic indicators, market trends, and breaking news. Let's take a quick tour of the key features.",
    icon: <Star className="h-6 w-6 text-yellow-500" />,
  },
  {
    target: '#today-feed',
    title: "Today's Feed",
    description:
      'Each day features different economic data and insights. The theme and content change based on the day of the week.',
    icon: <Star className="h-6 w-6 text-blue-500" />,
    position: 'bottom',
  },
  {
    target: '#favorites',
    title: 'Favorites',
    description:
      'Bookmark metrics by clicking the star icon. Your favorites appear here for quick access.',
    icon: <Star className="h-6 w-6 text-yellow-500 fill-yellow-500" />,
    position: 'bottom',
  },
  {
    title: 'Keyboard Shortcuts',
    description:
      'Press R to refresh data instantly. Use Cmd+K (or Ctrl+K) to open settings. These shortcuts work anywhere on the dashboard.',
    icon: <Keyboard className="h-6 w-6 text-purple-500" />,
  },
  {
    title: 'Stay Updated',
    description:
      "You're all set! The dashboard auto-refreshes every 5 minutes, but you can customize this in settings. Enjoy exploring your data!",
    icon: <RefreshCw className="h-6 w-6 text-green-500" />,
  },
]

export function OnboardingTour() {
  const { hasSeenTour, completeTour } = useSettings()
  const [currentStep, setCurrentStep] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Show tour after a brief delay if user hasn't seen it
    if (!hasSeenTour) {
      const timer = setTimeout(() => setIsVisible(true), 1000)
      return () => clearTimeout(timer)
    }
  }, [hasSeenTour])

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handleSkip = () => {
    handleComplete()
  }

  const handleComplete = () => {
    setIsVisible(false)
    completeTour()
  }

  const currentStepData = TOUR_STEPS[currentStep]

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
            onClick={handleSkip}
          />

          {/* Tour Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[101] w-full max-w-md"
          >
            <div className="bg-background border rounded-lg shadow-2xl p-6 mx-4">
              {/* Close button */}
              <button
                onClick={handleSkip}
                className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="h-4 w-4" />
              </button>

              {/* Icon */}
              <div className="flex items-center justify-center mb-4">
                {currentStepData.icon}
              </div>

              {/* Content */}
              <div className="text-center space-y-3 mb-6">
                <h2 className="text-xl font-semibold">{currentStepData.title}</h2>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {currentStepData.description}
                </p>
              </div>

              {/* Progress dots */}
              <div className="flex items-center justify-center gap-2 mb-6">
                {TOUR_STEPS.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentStep(index)}
                    className={`h-2 rounded-full transition-all ${
                      index === currentStep
                        ? 'w-8 bg-primary'
                        : 'w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50'
                    }`}
                  />
                ))}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between gap-3">
                <Button variant="ghost" size="sm" onClick={handleSkip}>
                  Skip tour
                </Button>
                <Button onClick={handleNext} size="sm" className="gap-2">
                  {currentStep < TOUR_STEPS.length - 1 ? (
                    <>
                      Next
                      <ArrowRight className="h-4 w-4" />
                    </>
                  ) : (
                    'Get started'
                  )}
                </Button>
              </div>

              {/* Step counter */}
              <p className="text-center text-xs text-muted-foreground mt-4">
                Step {currentStep + 1} of {TOUR_STEPS.length}
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
