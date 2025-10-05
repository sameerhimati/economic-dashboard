import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { newsletterService, type EmailConfig, type EmailConfigUpdate } from '@/services/newsletterService'
import { useAuth } from '@/hooks/useAuth'
import { toast } from 'sonner'
import { Loader2, CheckCircle2, XCircle, ExternalLink, Info, Eye, EyeOff } from 'lucide-react'

export function EmailConfiguration() {
  const { user } = useAuth()
  const [config, setConfig] = useState<EmailConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const [formData, setFormData] = useState<EmailConfigUpdate>({
    email_address: user?.email || '',
    email_app_password: '',
    imap_server: 'imap.gmail.com',
    imap_port: 993,
  })

  useEffect(() => {
    loadConfig()
  }, [])

  // Update email when user loads
  useEffect(() => {
    if (user?.email && !formData.email_address) {
      setFormData(prev => ({ ...prev, email_address: user.email }))
    }
  }, [user])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const data = await newsletterService.getEmailConfig()
      setConfig(data)

      // Populate form with existing data
      setFormData({
        email_address: data.email_address || '',
        email_app_password: '', // Never populate password
        imap_server: data.imap_server,
        imap_port: data.imap_port,
      })
    } catch (error) {
      console.error('Failed to load email config:', error)
      toast.error('Failed to load email configuration')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    // Validation
    if (!formData.email_address) {
      toast.error('Email address is required')
      return
    }

    // If not configured yet, password is required
    if (!config?.is_configured && !formData.email_app_password) {
      toast.error('App password is required for initial configuration')
      return
    }

    try {
      setSaving(true)

      // Only send fields that have values
      const updateData: EmailConfigUpdate = {
        imap_server: formData.imap_server,
        imap_port: formData.imap_port,
      }

      if (formData.email_address) {
        updateData.email_address = formData.email_address
      }

      if (formData.email_app_password) {
        updateData.email_app_password = formData.email_app_password
      }

      const updated = await newsletterService.updateEmailConfig(updateData)
      setConfig(updated)

      // Clear password field after successful save
      setFormData(prev => ({ ...prev, email_app_password: '' }))

      toast.success('Email configuration saved successfully')
    } catch (error: any) {
      console.error('Failed to save email config:', error)
      toast.error(error.response?.data?.detail || 'Failed to save email configuration')
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    try {
      setTesting(true)
      const result = await newsletterService.testEmailConnection(formData)

      if (result.success) {
        toast.success(result.message)
      } else {
        toast.error(result.message)
      }
    } catch (error) {
      console.error('Failed to test connection:', error)
      toast.error('Failed to test email connection')
    } finally {
      setTesting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await newsletterService.deleteEmailConfig()
      setConfig(null)
      setFormData({
        email_address: '',
        email_app_password: '',
        imap_server: 'imap.gmail.com',
        imap_port: 993,
      })
      toast.success('Email configuration deleted successfully')
      setShowDeleteDialog(false)
    } catch (error) {
      console.error('Failed to delete email config:', error)
      toast.error('Failed to delete email configuration')
    }
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
          <CardTitle>Configuration Status</CardTitle>
          <CardDescription>Current email configuration state</CardDescription>
        </CardHeader>
        <CardContent>
          {config?.is_configured ? (
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-medium">Email configured successfully</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <XCircle className="h-5 w-5" />
              <span className="font-medium">Email not configured</span>
            </div>
          )}
          {config?.email_address && (
            <p className="text-sm text-muted-foreground mt-2">
              Current email: {config.email_address}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Configuration Form */}
      <Card>
        <CardHeader>
          <CardTitle>Email Credentials</CardTitle>
          <CardDescription>
            Enter your Gmail credentials to fetch Bisnow newsletters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              placeholder="your.email@gmail.com"
              value={formData.email_address}
              onChange={(e) => setFormData({ ...formData, email_address: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Your Gmail address where you receive Bisnow newsletters
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="password">App Password</Label>
              <a
                href="https://myaccount.google.com/apppasswords"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline flex items-center gap-1"
              >
                <Info className="h-3 w-3" />
                Get app password
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder={config?.is_configured ? 'Leave blank to keep current password' : 'Enter Gmail app password'}
                value={formData.email_app_password}
                onChange={(e) => setFormData({ ...formData, email_app_password: e.target.value })}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <p className="text-xs text-muted-foreground">
              {config?.is_configured
                ? 'Only enter a new password if you want to update it'
                : '16-character password from Google App Passwords'
              }
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="imap-server">IMAP Server</Label>
              <Input
                id="imap-server"
                type="text"
                value={formData.imap_server}
                onChange={(e) => setFormData({ ...formData, imap_server: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="imap-port">IMAP Port</Label>
              <Input
                id="imap-port"
                type="number"
                value={formData.imap_port}
                onChange={(e) => setFormData({ ...formData, imap_port: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Configuration
            </Button>

            <Button onClick={handleTest} variant="outline" disabled={testing}>
              {testing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Test Connection
            </Button>

            {config?.is_configured && (
              <Button
                onClick={() => setShowDeleteDialog(true)}
                variant="destructive"
                className="ml-auto"
              >
                Delete Configuration
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will delete your email configuration. You will need to re-enter
              your credentials to fetch newsletters again. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
