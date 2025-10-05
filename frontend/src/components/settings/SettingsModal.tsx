import { useSettings } from '@/hooks/useSettings'
import { useBookmarks } from '@/hooks/useBookmarks'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Settings as SettingsIcon, Sun, Moon, Monitor, Trash2, Star } from 'lucide-react'
import { useState } from 'react'

interface SettingsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  theme: 'light' | 'dark' | 'system'
  onThemeChange: (theme: 'light' | 'dark' | 'system') => void
}

export function SettingsModal({ open, onOpenChange, theme, onThemeChange }: SettingsModalProps) {
  const {
    showTodayFeed,
    showFavorites,
    showMetrics,
    showBreakingNews,
    showWeeklySummary,
    refreshInterval,
    toggleSection,
    setRefreshInterval,
    resetSettings,
  } = useSettings()

  const { bookmarkedIds, clearBookmarks } = useBookmarks()
  const [showConfirmClear, setShowConfirmClear] = useState(false)

  const handleClearBookmarks = () => {
    clearBookmarks()
    setShowConfirmClear(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            Dashboard Settings
          </DialogTitle>
          <DialogDescription>
            Customize your dashboard experience and preferences
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Display Sections */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Display Sections</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="today-feed" className="flex-1 cursor-pointer">
                  Today's Feed
                  <p className="text-xs text-muted-foreground font-normal">
                    Show day-specific economic insights
                  </p>
                </Label>
                <Switch
                  id="today-feed"
                  checked={showTodayFeed}
                  onCheckedChange={() => toggleSection('showTodayFeed')}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="favorites" className="flex-1 cursor-pointer">
                  Favorites Section
                  <p className="text-xs text-muted-foreground font-normal">
                    Show your bookmarked metrics
                  </p>
                </Label>
                <Switch
                  id="favorites"
                  checked={showFavorites}
                  onCheckedChange={() => toggleSection('showFavorites')}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="metrics" className="flex-1 cursor-pointer">
                  Additional Metrics
                  <p className="text-xs text-muted-foreground font-normal">
                    Show all economic indicators
                  </p>
                </Label>
                <Switch
                  id="metrics"
                  checked={showMetrics}
                  onCheckedChange={() => toggleSection('showMetrics')}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="breaking-news" className="flex-1 cursor-pointer">
                  Breaking News
                  <p className="text-xs text-muted-foreground font-normal">
                    Show latest economic updates
                  </p>
                </Label>
                <Switch
                  id="breaking-news"
                  checked={showBreakingNews}
                  onCheckedChange={() => toggleSection('showBreakingNews')}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="weekly-summary" className="flex-1 cursor-pointer">
                  Weekly Summary
                  <p className="text-xs text-muted-foreground font-normal">
                    Show weekly market overview
                  </p>
                </Label>
                <Switch
                  id="weekly-summary"
                  checked={showWeeklySummary}
                  onCheckedChange={() => toggleSection('showWeeklySummary')}
                />
              </div>
            </div>
          </div>

          {/* Auto-refresh */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-semibold">Auto-refresh Interval</h3>
            <div className="space-y-2">
              <Label htmlFor="refresh-interval">
                Automatically refresh data
              </Label>
              <Select
                value={refreshInterval.toString()}
                onValueChange={(value) => setRefreshInterval(parseInt(value) as any)}
              >
                <SelectTrigger id="refresh-interval">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Manual only</SelectItem>
                  <SelectItem value="1">Every 1 minute</SelectItem>
                  <SelectItem value="5">Every 5 minutes</SelectItem>
                  <SelectItem value="10">Every 10 minutes</SelectItem>
                  <SelectItem value="30">Every 30 minutes</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                {refreshInterval === 0
                  ? 'Data will only refresh when you click the refresh button'
                  : `Data will automatically refresh every ${refreshInterval} minute${refreshInterval > 1 ? 's' : ''}`}
              </p>
            </div>
          </div>

          {/* Theme */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-semibold">Appearance</h3>
            <div className="space-y-2">
              <Label>Theme</Label>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onThemeChange('light')}
                  className="gap-2"
                >
                  <Sun className="h-4 w-4" />
                  Light
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onThemeChange('dark')}
                  className="gap-2"
                >
                  <Moon className="h-4 w-4" />
                  Dark
                </Button>
                <Button
                  variant={theme === 'system' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onThemeChange('system')}
                  className="gap-2"
                >
                  <Monitor className="h-4 w-4" />
                  System
                </Button>
              </div>
            </div>
          </div>

          {/* Bookmarks Management */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-semibold">Saved Items</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">
                    {bookmarkedIds.size} bookmarked metric{bookmarkedIds.size !== 1 ? 's' : ''}
                  </span>
                </div>
                {bookmarkedIds.size > 0 && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => setShowConfirmClear(true)}
                    className="gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    Clear all
                  </Button>
                )}
              </div>
              {showConfirmClear && (
                <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 space-y-2">
                  <p className="text-sm text-destructive font-medium">
                    Clear all bookmarks?
                  </p>
                  <p className="text-xs text-muted-foreground">
                    This will remove all {bookmarkedIds.size} bookmarked metrics. This action cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleClearBookmarks}
                    >
                      Confirm
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowConfirmClear(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Reset */}
          <div className="border-t pt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={resetSettings}
              className="w-full"
            >
              Reset to defaults
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
