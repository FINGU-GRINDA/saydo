import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slack, Calendar, Mail } from "lucide-react" // Using Lucide for consistency

const integrations = [
  { name: "Google Calendar", Icon: Calendar, description: "Automatically schedule meetings from calls." },
  { name: "Slack", Icon: Slack, description: "Send call summaries to channels." },
  { name: "Gmail", Icon: Mail, description: "Draft and send follow-up emails." },
]

export function IntegrationsScreen() {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">Integrations</h2>
      <p className="text-gray-600 mb-6">Connect Saydo to your favorite tools to automate your workflow.</p>
      <div className="space-y-4">
        {integrations.map((integration) => (
          <Card key={integration.name} className="bg-white shadow-sm border-gray-200">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-4">
                <integration.Icon className="w-6 h-6 text-gray-500" />
                <div>
                  <CardTitle className="text-base">{integration.name}</CardTitle>
                  <CardDescription>{integration.description}</CardDescription>
                </div>
              </div>
              <Button variant="outline">Connect</Button>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  )
}
