# Adding New Actions to Saydo CallOps

This guide explains how to add new action types to the AI agent system.

## Overview

Actions in Saydo CallOps are AI-generated tasks that can be executed after user approval. Each action type has:
- A definition in the AI agent
- An executor in the backend
- A UI component in the frontend

## Step 1: Define the Action Type

### Update Action Types

In `server/app/models/meeting.py`, add your new action type:

```python
class ActionType(str, Enum):
    CALENDAR_EVENT = "calendar_event"
    EMAIL = "email"
    SHEET_UPDATE = "sheet_update"
    TODO = "todo"
    DOCUMENT_CREATE = "document_create"
    SLACK_MESSAGE = "slack_message"  # New action type
```

## Step 2: Add AI Tool Definition

### Update OpenAI Agent

In `server/app/services/openai_agent.py`, add the tool definition:

```python
def _get_tools(self) -> List[Dict]:
    tools = []
    
    # Existing tools...
    
    if "slack_message" in self.enabled_capabilities:
        tools.append({
            "type": "function",
            "function": {
                "name": "send_slack_message",
                "description": "Send a message to a Slack channel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Slack channel name (e.g., #general)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content"
                        },
                        "thread_ts": {
                            "type": "string",
                            "description": "Thread timestamp for replies (optional)"
                        }
                    },
                    "required": ["channel", "message"]
                }
            }
        })
    
    return tools
```

### Handle Tool Response

Add handling in `_create_action_from_tool_call`:

```python
elif function_name == "send_slack_message":
    return {
        "type": ActionType.SLACK_MESSAGE,
        "description": f"Send Slack message to {args.get('channel')}",
        "details": args
    }
```

## Step 3: Implement Action Executor

### Add Executor Method

In `server/app/services/action_executor.py`, add the execution logic:

```python
async def execute_slack_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to Slack channel."""
    try:
        # Import Slack SDK
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        # Initialize Slack client with user's token
        client = WebClient(token=self.slack_token)
        
        # Send message
        result = client.chat_postMessage(
            channel=args.get('channel'),
            text=args.get('message'),
            thread_ts=args.get('thread_ts')  # Optional for threading
        )
        
        return {
            "success": True,
            "message_ts": result["ts"],
            "channel": result["channel"]
        }
        
    except SlackApiError as e:
        raise Exception(f"Slack API error: {e.response['error']}")
```

### Update Main Executor

Add to the `execute_action` method:

```python
elif action.type == ActionType.SLACK_MESSAGE:
    return await self.execute_slack_message(action.details)
```

## Step 4: Add Frontend Components

### Create Action Card Component

Create `client/components/saydo/actions/slack-action-card.tsx`:

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageSquare, Check, X } from "lucide-react"

interface SlackActionCardProps {
  action: {
    id: string
    description: string
    details: {
      channel: string
      message: string
    }
    status: 'pending' | 'completed' | 'failed'
  }
  onApprove: () => void
  onReject: () => void
}

export function SlackActionCard({ action, onApprove, onReject }: SlackActionCardProps) {
  return (
    <Card className="border-purple-200 bg-purple-50/50">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-purple-600" />
            <CardTitle className="text-base">Slack Message</CardTitle>
          </div>
          {action.status === 'pending' && (
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={onApprove}
                className="h-8 w-8 p-0"
              >
                <Check className="h-4 w-4 text-green-600" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onReject}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4 text-red-600" />
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <CardDescription className="text-sm">
          <strong>Channel:</strong> {action.details.channel}
        </CardDescription>
        <div className="mt-2 p-2 bg-white rounded border border-purple-200">
          <p className="text-sm">{action.details.message}</p>
        </div>
      </CardContent>
    </Card>
  )
}
```

### Update Action Renderer

In the component that renders actions, add the new action type:

```tsx
import { SlackActionCard } from './slack-action-card'

// In your action rendering logic
{action.type === 'slack_message' && (
  <SlackActionCard
    action={action}
    onApprove={() => handleApprove(action.id)}
    onReject={() => handleReject(action.id)}
  />
)}
```

## Step 5: Add Integration Settings

### Update Agent Preferences

Allow users to enable/disable the new action type:

```tsx
// In AI Agent settings component
<div className="flex items-center justify-between">
  <div className="space-y-0.5">
    <Label>Slack Messages</Label>
    <p className="text-sm text-muted-foreground">
      Send messages to Slack channels
    </p>
  </div>
  <Switch
    checked={capabilities.includes('slack_message')}
    onCheckedChange={(checked) => {
      if (checked) {
        addCapability('slack_message')
      } else {
        removeCapability('slack_message')
      }
    }}
  />
</div>
```

## Step 6: Add Configuration

### Environment Variables

Add to `.env`:

```bash
# Slack Integration
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
```

### User Token Storage

Store user's Slack token in Firebase:

```python
# In authentication flow
user_data = {
    "slack_token": slack_oauth_response["access_token"],
    "slack_team_id": slack_oauth_response["team"]["id"],
    "slack_team_name": slack_oauth_response["team"]["name"]
}
```

## Step 7: Test the New Action

### Unit Tests

Create `server/tests/test_slack_action.py`:

```python
import pytest
from app.services.action_executor import ActionExecutor
from app.models.meeting import ActionType

@pytest.mark.asyncio
async def test_slack_message_execution():
    executor = ActionExecutor(user_id="test_user")
    
    action = {
        "type": ActionType.SLACK_MESSAGE,
        "details": {
            "channel": "#general",
            "message": "Test message from Saydo"
        }
    }
    
    result = await executor.execute_action(action)
    assert result["success"] is True
    assert "message_ts" in result
```

### Integration Tests

Test the full flow:

1. Create a meeting with relevant conversation
2. Process with AI agent
3. Verify Slack action is generated
4. Execute action and verify in Slack

## Best Practices

### 1. Error Handling

Always handle API failures gracefully:

```python
try:
    result = await external_api_call()
except ExternalAPIError as e:
    logger.error(f"API call failed: {e}")
    return {
        "success": False,
        "error": str(e)
    }
```

### 2. User Feedback

Provide clear status updates:

```tsx
{action.status === 'executing' && (
  <div className="flex items-center gap-2">
    <Loader2 className="h-4 w-4 animate-spin" />
    <span className="text-sm text-muted-foreground">
      Sending to Slack...
    </span>
  </div>
)}
```

### 3. Validation

Validate action parameters:

```python
def validate_slack_action(args: Dict[str, Any]) -> bool:
    if not args.get('channel', '').startswith('#'):
        raise ValueError("Channel must start with #")
    if len(args.get('message', '')) > 4000:
        raise ValueError("Message too long")
    return True
```

### 4. Permissions

Check user has necessary permissions:

```python
if not user_has_slack_connected(user_id):
    raise PermissionError("Please connect your Slack account first")
```

## Common Action Types to Add

### 1. CRM Update
- Update Salesforce/HubSpot records
- Log customer interactions
- Create new leads

### 2. Project Management
- Create Jira tickets
- Update Trello cards
- Add Asana tasks

### 3. Communication
- Send SMS via Twilio
- Post to Microsoft Teams
- Update Discord channels

### 4. Documentation
- Create Notion pages
- Update Confluence
- Generate PDFs

### 5. Analytics
- Log events to Mixpanel
- Update Google Analytics
- Send to data warehouse

## Troubleshooting

### Action not appearing in AI suggestions
- Check tool definition in `_get_tools()`
- Verify capability is enabled
- Test with explicit prompts

### Execution failing
- Check API credentials
- Verify user has connected integration
- Look for rate limiting

### UI not updating
- Ensure GraphQL schema is updated
- Check WebSocket connection
- Verify action status updates

## Next Steps

- Read [AI Capabilities Guide](./ai-capabilities.md)
- Learn about [Custom Integrations](../integrations/custom.md)
- Explore [Testing Strategies](./testing.md)