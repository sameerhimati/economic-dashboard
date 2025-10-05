import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { EmailConfiguration } from '@/components/settings/EmailConfiguration'
import { NewsletterPreferencesTab } from '@/components/settings/NewsletterPreferencesTab'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings as SettingsIcon, Mail, Bell } from 'lucide-react'

export function Settings() {
  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Header */}
          <div>
            <div className="flex items-center gap-3 mb-2">
              <SettingsIcon className="h-8 w-8 text-primary" />
              <h1 className="text-4xl font-bold tracking-tight">Settings</h1>
            </div>
            <p className="text-muted-foreground">
              Configure your email credentials and newsletter preferences
            </p>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="email" className="space-y-6">
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="email" className="gap-2">
                <Mail className="h-4 w-4" />
                Email Configuration
              </TabsTrigger>
              <TabsTrigger value="preferences" className="gap-2">
                <Bell className="h-4 w-4" />
                Newsletter Preferences
              </TabsTrigger>
            </TabsList>

            <TabsContent value="email" className="space-y-6">
              <EmailConfiguration />
            </TabsContent>

            <TabsContent value="preferences" className="space-y-6">
              <NewsletterPreferencesTab />
            </TabsContent>
          </Tabs>
        </div>
      </PageTransition>
    </Layout>
  )
}
