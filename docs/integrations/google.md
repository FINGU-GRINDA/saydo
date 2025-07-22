# Google Workspace Integration Setup

This guide walks you through setting up Google Workspace integration for Saydo CallOps.

## Prerequisites

- Google Cloud Platform account
- Google Workspace or Gmail account
- Admin access to create OAuth applications

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Saydo CallOps")
4. Click "Create"

## Step 2: Enable Required APIs

Enable the following APIs in your project:

1. **Google Calendar API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

2. **Gmail API**
   - Search for "Gmail API"
   - Click "Enable"

3. **Google Sheets API**
   - Search for "Google Sheets API"
   - Click "Enable"

4. **Google Tasks API**
   - Search for "Google Tasks API"
   - Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: "Saydo CallOps"
   - User support email: your email
   - Developer contact: your email

4. Add scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/tasks`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`

5. Add test users (your email addresses)
6. Save and continue

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Configure:
   - Name: "Saydo CallOps Web Client"
   - Authorized JavaScript origins:
     ```
     http://localhost:3000
     https://your-domain.com
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:8000/api/auth/google/callback
     https://your-domain.com/api/auth/google/callback
     ```

5. Click "Create"
6. Save the Client ID and Client Secret

## Step 5: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Optional: Set custom scopes
GOOGLE_SCOPES="openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/tasks"
```

## Step 6: Test the Integration

1. Start your application:
   ```bash
   cd client && npm run dev
   cd server && uv run python -m app.main
   ```

2. Navigate to http://localhost:3000
3. Click on "AI Agent" settings
4. Click "Connect Google Account"
5. Authorize the requested permissions
6. You should see a success message

## Usage Examples

### Creating a Calendar Event

Once connected, the AI can create calendar events from meeting conversations:

```
User: "Let's meet next Tuesday at 2pm"
AI Action: Creates calendar event for next Tuesday at 2:00 PM
```

### Sending Follow-up Emails

The AI can draft and send emails based on meeting context:

```
User: "I'll send you the proposal by Friday"
AI Action: Drafts reminder email about proposal deadline
```

### Updating Google Sheets

Track meeting outcomes in spreadsheets:

```
User: "Add this to our project tracker"
AI Action: Updates designated Google Sheet with meeting notes
```

## Troubleshooting

### "Access blocked" error
- Ensure your app is in testing mode or published
- Add user emails to test users list

### "Invalid redirect URI" error
- Double-check redirect URIs match exactly
- Include both http://localhost and production URLs

### "Insufficient permissions" error
- User may need to re-authorize with updated scopes
- Check that all required APIs are enabled

### Token expiration
- Tokens are automatically refreshed
- If issues persist, user can reconnect account

## Security Best Practices

1. **Never commit credentials**
   - Keep `.env` file in `.gitignore`
   - Use environment variables in production

2. **Limit scopes**
   - Only request necessary permissions
   - Explain why each permission is needed

3. **Secure storage**
   - Tokens are encrypted in Firebase
   - Use HTTPS in production

4. **Regular audits**
   - Review connected accounts periodically
   - Revoke unused tokens

## Advanced Configuration

### Custom Calendar Selection

To use a specific calendar instead of primary:

```python
# In action_executor.py
calendar_id = 'your-calendar-id@group.calendar.google.com'
service.events().insert(calendarId=calendar_id, body=event).execute()
```

### Email Templates

Create custom email templates:

```python
# In openai_agent.py
email_template = """
Subject: {subject}

Hi {recipient},

{body}

Best regards,
{sender}
"""
```

### Batch Operations

For multiple actions:

```python
# Use Google API batch requests
batch = service.new_batch_http_request()
batch.add(service.events().insert(...))
batch.add(service.tasks().insert(...))
batch.execute()
```

## Next Steps

- Set up [Slack Integration](./slack.md)
- Configure [Microsoft Teams](./teams.md)
- Add [Custom Webhooks](./webhooks.md)