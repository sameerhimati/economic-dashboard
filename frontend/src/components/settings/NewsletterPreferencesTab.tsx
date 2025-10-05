import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { newsletterService, type NewsletterPreferences } from '@/services/newsletterService'
import { toast } from 'sonner'
import { Loader2, Save } from 'lucide-react'

export function NewsletterPreferencesTab() {
  const [preferences, setPreferences] = useState<NewsletterPreferences | null>(null)
  const [availableCategories, setAvailableCategories] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [fetchEnabled, setFetchEnabled] = useState(false)

  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = async () => {
    try {
      setLoading(true)

      // Load both preferences and available categories in parallel
      const [prefs, categories] = await Promise.all([
        newsletterService.getNewsletterPreferences(),
        newsletterService.getAvailableCategories(),
      ])

      setPreferences(prefs)
      setAvailableCategories(categories)
      setSelectedCategories(prefs.bisnow_categories)
      setFetchEnabled(prefs.fetch_enabled)
    } catch (error) {
      console.error('Failed to load preferences:', error)
      toast.error('Failed to load newsletter preferences')
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
  }

  const handleSave = async () => {
    try {
      setSaving(true)

      const updated = await newsletterService.updateNewsletterPreferences({
        bisnow_categories: selectedCategories,
        fetch_enabled: fetchEnabled,
      })

      setPreferences(updated)
      toast.success('Newsletter preferences saved successfully')
    } catch (error: any) {
      console.error('Failed to save preferences:', error)
      toast.error(error.response?.data?.detail || 'Failed to save newsletter preferences')
    } finally {
      setSaving(false)
    }
  }

  const handleSelectAll = () => {
    setSelectedCategories([...availableCategories])
  }

  const handleDeselectAll = () => {
    setSelectedCategories([])
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card>
        <CardHeader>
          <CardTitle>Preferences Overview</CardTitle>
          <CardDescription>Current newsletter subscription settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Automatic Fetching</Label>
              <p className="text-sm text-muted-foreground">
                Enable automatic newsletter fetching (coming soon)
              </p>
            </div>
            <Switch
              checked={fetchEnabled}
              onCheckedChange={setFetchEnabled}
              disabled
            />
          </div>

          <div className="pt-2">
            <Label>Selected Categories</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {selectedCategories.length > 0 ? (
                selectedCategories.map(category => (
                  <Badge key={category} variant="secondary">
                    {category}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No categories selected</p>
              )}
            </div>
          </div>

          {preferences?.last_fetch && (
            <div className="pt-2">
              <Label>Last Fetch</Label>
              <p className="text-sm text-muted-foreground mt-1">
                {new Date(preferences.last_fetch).toLocaleString()}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Category Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Bisnow Newsletter Categories</CardTitle>
              <CardDescription>
                Select the newsletter categories you want to track
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                Select All
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeselectAll}
              >
                Deselect All
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableCategories.map(category => (
              <div
                key={category}
                className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors"
              >
                <Checkbox
                  id={`category-${category}`}
                  checked={selectedCategories.includes(category)}
                  onCheckedChange={() => handleCategoryToggle(category)}
                />
                <Label
                  htmlFor={`category-${category}`}
                  className="flex-1 cursor-pointer"
                >
                  {category}
                </Label>
              </div>
            ))}
          </div>

          {availableCategories.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p>No categories available</p>
              <p className="text-sm mt-1">
                Categories will appear after you fetch newsletters for the first time
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving} size="lg">
          {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          <Save className="mr-2 h-4 w-4" />
          Save Preferences
        </Button>
      </div>
    </div>
  )
}
