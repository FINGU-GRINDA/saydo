from openai import OpenAI
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from config import settings
from app.models.meeting import ActionType, MeetingAction
from app.services.firebase_service import firebase_service
import uuid


class MeetingAgent:
    def __init__(self, user_id: str = None):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.user_id = user_id
        self.enabled_capabilities = []
        self.tools = []
    
    async def initialize_capabilities(self):
        """Load user's enabled capabilities from Firebase"""
        if self.user_id:
            try:
                preferences = await firebase_service.get_agent_preferences(self.user_id)
                if preferences and preferences.get('capabilities'):
                    self.enabled_capabilities = [
                        cap['id'] for cap in preferences['capabilities'] 
                        if cap.get('enabled', False)
                    ]
                else:
                    # Default capabilities if no preferences found
                    self.enabled_capabilities = ["summary", "todo"]
            except Exception as e:
                print(f"Error loading capabilities for user {self.user_id}: {e}")
                # Fallback to default capabilities
                self.enabled_capabilities = ["summary", "todo"]
        else:
            # Default capabilities for users without ID
            self.enabled_capabilities = ["summary", "todo"]
        
        # Build tools based on enabled capabilities
        self.tools = self._define_tools()
    
    def _define_tools(self):
        all_tools = {
            "calendar": {
                "type": "function",
                "function": {
                    "name": "schedule_calendar_event",
                    "description": "Schedule a new event in Google Calendar",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Event title"
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time in ISO format"
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of attendee emails"
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description"
                            }
                        },
                        "required": ["title", "start_time", "end_time", "attendees", "description"],
                        "additionalProperties": False
                    }
                }
            },
            "email": {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email via Gmail",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of recipient emails"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body"
                            }
                        },
                        "required": ["to", "subject", "body"],
                        "additionalProperties": False
                    }
                }
            },
            "sheets": {
                "type": "function",
                "function": {
                    "name": "update_google_sheet",
                    "description": "Add or update data in a Google Sheet",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sheet_id": {
                                "type": "string",
                                "description": "Google Sheet ID"
                            },
                            "range": {
                                "type": "string",
                                "description": "Cell range (e.g., 'A1:B2')"
                            },
                            "values": {
                                "type": "array",
                                "items": {"type": "array", "items": {"type": "string"}},
                                "description": "2D array of values to insert"
                            }
                        },
                        "required": ["sheet_id", "range", "values"],
                        "additionalProperties": False
                    }
                }
            },
            "docs": {
                "type": "function",
                "function": {
                    "name": "create_google_doc",
                    "description": "Create a new Google Doc with meeting notes",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Document title"
                            },
                            "content": {
                                "type": "string",
                                "description": "Document content in markdown format"
                            }
                        },
                        "required": ["title", "content"],
                        "additionalProperties": False
                    }
                }
            }
        }
        
        # Always include todo capability - it doesn't require external integrations
        all_tools["todo"] = {
            "type": "function",
            "function": {
                "name": "create_todo",
                "description": "Create a todo item from the meeting",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Todo title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Todo description"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Person responsible"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format"
                        }
                    },
                    "required": ["title", "description", "assignee", "due_date"],
                    "additionalProperties": False
                }
            }
        }
        
        # Return only enabled tools
        enabled_tools = []
        for capability, tool in all_tools.items():
            if capability in self.enabled_capabilities or capability == "todo":
                enabled_tools.append(tool)
        
        return enabled_tools
    
    async def process_transcript(self, transcript: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Ensure capabilities are loaded
        if not self.enabled_capabilities:
            await self.initialize_capabilities()
        
        # Build dynamic system prompt based on enabled capabilities
        capability_prompts = {
            "summary": "Generate concise meeting summaries highlighting key decisions and discussions",
            "calendar": "Create calendar events for scheduled meetings with all relevant details",
            "email": "Draft professional follow-up emails based on meeting content", 
            "sheets": "Prepare structured data for spreadsheet updates",
            "docs": "Create comprehensive meeting documentation",
            "todo": "Extract actionable tasks and todo items from conversations"
        }
        
        enabled_prompts = [prompt for cap, prompt in capability_prompts.items() 
                          if cap in self.enabled_capabilities]
        
        # Always include summary capability
        if "summary" not in self.enabled_capabilities:
            enabled_prompts.insert(0, capability_prompts["summary"])
        
        from datetime import datetime, timedelta
        current_date = datetime.utcnow()
        tomorrow = current_date + timedelta(days=1)
        
        system_prompt = f"""You are an AI meeting assistant that analyzes meeting transcripts.
        
        Current date/time: {current_date.strftime('%Y-%m-%d %H:%M UTC')}
        
        Your enabled capabilities:
        {chr(10).join(f'- {prompt}' for prompt in enabled_prompts)}
        
        Guidelines for Summary:
        - Keep summaries concise but informative (2-4 sentences)
        - Use simple, clear language
        - Format in clean Markdown without excessive headers
        - Focus on what was discussed and any decisions made
        
        Guidelines for Actions:
        - Only extract actions that were explicitly mentioned
        - Include specific details like dates, times, and assignees
        - Be precise about what needs to be done
        - Extract TODO items for personal reminders (e.g., "feed the cat", "run updates")
        - Extract calendar events for scheduled meetings with times
        - Only use tools that correspond to your enabled capabilities
        
        IMPORTANT: Do NOT list actions in your text summary. Use the provided tool functions to create actions.
        - For tasks/reminders: use the create_todo function
        - For calendar events: use the schedule_calendar_event function
        - For emails: use the send_email function
        Only mention in the summary that actions were identified, but execute them via tools
        
        IMPORTANT Date Guidelines:
        - When scheduling calendar events, use appropriate future dates
        - If a specific date is mentioned (like "Wednesday"), calculate the next occurrence from today ({current_date.strftime('%Y-%m-%d')})
        - If time is mentioned without timezone (like "12 pm"), treat it as the user's local time
        - Google Calendar will handle timezone conversion based on the user's calendar settings
        - Default meeting duration should be 30 minutes unless specified
        - All dates must be in ISO 8601 format (e.g., {tomorrow.strftime('%Y-%m-%dT%H:%M:%S')})
        - Do NOT add 'Z' suffix - let Google Calendar handle timezone
        - When user says "12 pm", create the event for 12:00 in their local time
        
        For the summary, use this format:
        Brief overview of what was discussed in 2-4 sentences. Focus on key points and any decisions made."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please analyze this meeting transcript. First, provide a concise summary of what was discussed (2-4 sentences). Then, use the appropriate tool functions to create any actions mentioned in the meeting. Do not list the actions in your text response - use the tools instead.\n\nTranscript:\n{transcript}"}
        ]

        try:
            # Only include tools if we have enabled capabilities beyond just summary
            tools = self.tools if len(self.enabled_capabilities) > 1 or "summary" not in self.enabled_capabilities else None
            
            # Debug log tools
            print(f"🔧 Enabled capabilities: {self.enabled_capabilities}")
            print(f"🔧 Number of tools available: {len(self.tools) if self.tools else 0}")
            if tools:
                print(f"🔧 Tools being passed to AI: {[t['function']['name'] for t in tools]}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                temperature=0.1
            )

            # Extract summary from the response
            summary = response.choices[0].message.content
            
            # Log the AI response for debugging
            print(f"📝 AI Response Summary: {summary[:100] if summary else 'None'}...")
            
            # If no summary was provided, create a basic one
            if not summary or summary.strip() == "":
                summary = "Meeting transcript analyzed. No specific discussion points or decisions were identified in this meeting."
                print("⚠️  Warning: AI did not provide a summary for the meeting")
            
            # Process tool calls if any
            actions = []
            if response.choices[0].message.tool_calls:
                print(f"🎯 AI made {len(response.choices[0].message.tool_calls)} tool calls")
                for tool_call in response.choices[0].message.tool_calls:
                    try:
                        print(f"🔨 Processing tool call: {tool_call.function.name}")
                        action = self._create_action_from_tool_call(tool_call)
                        if action:
                            actions.append(action)
                            print(f"✅ Created action: {action['description']}")
                    except Exception as e:
                        print(f"❌ Error processing tool call {tool_call.function.name}: {e}")
                        continue
            else:
                print("⚠️  AI did not make any tool calls")

            return {
                "summary": summary,
                "actions": actions,
                "enabled_capabilities": self.enabled_capabilities
            }

        except Exception as e:
            print(f"Error processing transcript: {e}")
            return {
                "summary": "Error processing meeting transcript. Please try again.",
                "actions": [],
                "enabled_capabilities": self.enabled_capabilities
            }

    def _create_action_from_tool_call(self, tool_call) -> Optional[Dict[str, Any]]:
        """Convert OpenAI tool call to action format"""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Map function names to action types
        action_type_mapping = {
            "schedule_calendar_event": ActionType.CALENDAR_EVENT,
            "send_email": ActionType.EMAIL,
            "update_google_sheet": ActionType.SHEET_UPDATE,
            "create_google_doc": ActionType.DOCUMENT_CREATE,
            "create_todo": ActionType.TODO
        }
        
        action_type = action_type_mapping.get(function_name)
        if not action_type:
            return None
        
        # Create action description based on type
        description = self._generate_action_description(function_name, arguments)
        
        return {
            "id": str(uuid.uuid4()),
            "type": action_type.value,  # Changed from action_type to type for frontend compatibility
            "action_type": action_type.value,  # Keep for backend compatibility
            "description": description,
            "details": {
                "function": function_name,
                "arguments": arguments
            },
            "status": "pending",
            "created_at": datetime.utcnow()
        }
    
    def _generate_action_description(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """Generate human-readable description for action"""
        if function_name == "schedule_calendar_event":
            title = arguments.get("title", "Meeting")
            start_time = arguments.get("start_time", "")
            return f"Schedule '{title}' for {start_time}"
            
        elif function_name == "send_email":
            recipients = arguments.get("to", [])
            subject = arguments.get("subject", "Follow-up")
            return f"Send email '{subject}' to {', '.join(recipients[:2])}{'...' if len(recipients) > 2 else ''}"
            
        elif function_name == "update_google_sheet":
            sheet_id = arguments.get("sheet_id", "sheet")
            return f"Update Google Sheet with meeting data"
            
        elif function_name == "create_google_doc":
            title = arguments.get("title", "Meeting Notes")
            return f"Create document '{title}'"
            
        elif function_name == "create_todo":
            title = arguments.get("title", "Task")
            assignee = arguments.get("assignee", "")
            return f"Create todo: '{title}'" + (f" for {assignee}" if assignee else "")
            
        return f"Execute {function_name}"