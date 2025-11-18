# Meeting Management System Documentation

## Overview

The Meeting Management System is an integrated AI-powered solution for scheduling and managing meetings within the AI calling platform. It provides automatic conflict detection, natural language time parsing, and a web-based administrative interface.

## Features

### 1. Automatic Meeting Detection
- AI automatically detects when a caller wants to schedule a meeting
- Supports various Czech expressions: "schůzka", "sejít se", "potkat se", etc.
- Natural language understanding for date/time expressions

### 2. Time Parsing
The system understands Czech time expressions:
- **Relative days**: "dnes", "zítra", "pozítří"
- **Weekdays**: "pondělí", "úterý", "středa", "čtvrtek", "pátek"
- **Time of day**: "ráno" (9:00), "dopoledne" (10:00), "odpoledne" (14:00), "večer" (18:00)
- **Specific times**: "ve 14:00", "ve 3" (converts to 15:00)

### 3. Conflict Detection
- Automatic checking of overlapping meetings
- Minimum 24-hour spacing between meetings (configurable)
- Blocked time periods (e.g., "středa 8-14h nemám čas")

### 4. Alternative Suggestions
When requested time is unavailable, AI automatically suggests 2-3 alternative times:
```
"Bohužel středa je obsazená. Šlo by čtvrtek 15:00 nebo pátek 14:00?"
```

### 5. Web Dashboard (`/admin/meetings`)
- Overview of all scheduled meetings
- Statistics (total, upcoming, by status)
- Add/edit/delete meetings
- Block time periods for unavailability
- Calendar view with visual representation

## Database Schema

### Meetings Table
```sql
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY,
    call_sid TEXT,                -- Twilio call ID (optional)
    contact_name TEXT NOT NULL,   -- Name of the contact
    contact_phone TEXT NOT NULL,  -- Phone number
    meeting_datetime TEXT NOT NULL, -- ISO format datetime
    location_type TEXT,           -- 'u_nas', 'u_nich', 'online'
    location_details TEXT,        -- Additional location info
    status TEXT DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
    followup_person TEXT,         -- Who will follow up (default: 'Ondřej')
    notes TEXT,                   -- Additional notes
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Availability Blocks Table
```sql
CREATE TABLE availability_blocks (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,           -- Date (YYYY-MM-DD)
    time_from TEXT NOT NULL,      -- Start time (HH:MM)
    time_to TEXT NOT NULL,        -- End time (HH:MM)
    reason TEXT,                  -- Reason for blocking
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### GET `/admin/meetings`
Dashboard with meeting overview

### GET `/admin/meetings/api/meetings`
Get list of meetings with optional filters:
- `status`: Filter by status
- `from_date`: From date (ISO format)
- `to_date`: To date (ISO format)

**Response:**
```json
{
  "success": true,
  "meetings": [
    {
      "id": 1,
      "contact_name": "Jan Novák",
      "meeting_datetime": "2025-11-20T14:00:00",
      "status": "scheduled"
    }
  ]
}
```

### POST `/admin/meetings/api/meetings`
Create new meeting

**Request:**
```json
{
  "contact_name": "Jan Novák",
  "contact_phone": "+420123456789",
  "meeting_datetime": "2025-11-20T14:00:00",
  "location_type": "online",
  "followup_person": "Ondřej",
  "notes": "Initial consultation"
}
```

### PUT `/admin/meetings/api/meetings/{id}`
Update existing meeting

### DELETE `/admin/meetings/api/meetings/{id}`
Delete meeting

### POST `/admin/meetings/api/check-availability`
Check if a time slot is available

**Request:**
```json
{
  "datetime": "2025-11-20T14:00:00"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "available": false,
    "datetime": "2025-11-20T14:00:00",
    "conflicts": [...],
    "alternatives": [
      "2025-11-21T14:00:00",
      "2025-11-21T16:00:00"
    ]
  }
}
```

### GET/POST/DELETE `/admin/meetings/api/availability-blocks`
Manage time blocks for unavailability

### GET `/admin/meetings/calendar`
Visual calendar view with all meetings and blocks

## Usage Examples

### Python API

```python
from database.meetings_db import MeetingsDB
from services.meeting_scheduler import MeetingScheduler

# Initialize
db = MeetingsDB()
scheduler = MeetingScheduler()

# Schedule a meeting
meeting_id = scheduler.schedule_meeting(
    contact_name="Jan Novák",
    contact_phone="+420123456789",
    meeting_datetime="2025-11-20T14:00:00",
    location_type="online",
    notes="Demo call"
)

# Check availability
result = scheduler.suggest_meeting_time("2025-11-20T14:00:00")
if result['available']:
    print("Time is available!")
else:
    print(f"Conflicts: {result['conflicts']}")
    print(f"Alternatives: {result['alternatives']}")

# Parse time from natural language
text = "Můžeme se sejít ve středu ve 3?"
datetime_iso = scheduler.parse_time_from_text(text)
print(f"Parsed: {datetime_iso}")

# Format for Czech output
formatted = scheduler.format_datetime_czech(datetime_iso)
print(f"Czech: {formatted}")  # "středa 20. listopadu ve 15:00"
```

### AI Conversation Flow

```
User: "Můžeme se sejít zítra odpoledne?"
AI detects meeting intent → checks availability → responds

If available:
AI: "Výborně! Zítra 14:00 mám volno. Kde byste preferoval schůzku - u vás, u nás nebo online?"

If conflict:
AI: "Bohužel zítra už mám schůzku. Šlo by pozítří 14:00 nebo ve čtvrtek 15:00?"

User: "Čtvrtek 15:00 by bylo super."
AI: "Skvělé! Mám to zaznamenané - čtvrtek 22. listopadu ve 15:00. Zavolá vám Ondřej na potvrzení."
```

## Configuration

### Meeting Rules (database/knowledge_base.py)
```python
"rules": {
    "min_spacing_hours": 24,  # Minimum hours between meetings
    "default_duration_minutes": 60,  # Default meeting length
    "business_hours": {
        "start": 8,  # Start of business day
        "end": 18    # End of business day
    },
    "default_followup": "Ondřej"  # Default follow-up person
}
```

## Web Interface

### Dashboard Features
1. **Statistics Overview**
   - Total meetings
   - Upcoming meetings
   - Meetings by status

2. **Quick Actions**
   - Add new meeting
   - Block time period
   - View calendar

3. **Meeting Management**
   - View upcoming meetings (7 days)
   - Edit meeting details
   - Delete/cancel meetings
   - Update meeting status

4. **Time Blocking**
   - Add unavailable time periods
   - Specify reason for blocking
   - Remove blocks when no longer needed

### Calendar View
- Monthly grid layout
- Visual indicators for meetings and blocks
- Color-coded by type (meeting/block/today)
- Click to view details
- Navigate between months

## Integration with AI Engine

The meeting system is automatically integrated with the AI conversation engine:

1. **Intent Detection**: AI recognizes meeting-related keywords
2. **Auto-Response**: Generates appropriate responses based on availability
3. **Context Tracking**: Maintains conversation context throughout scheduling
4. **Knowledge Base**: Uses meeting-specific responses and examples

## Best Practices

1. **Always check availability** before confirming a meeting
2. **Use ISO format** for all datetime values in API calls
3. **Set blocks in advance** for known unavailable periods
4. **Update meeting status** after completion or cancellation
5. **Include follow-up person** for better tracking

## Troubleshooting

### Issue: Time parsing not working correctly
- Check that text includes recognizable keywords
- Verify Czech language input
- Use specific times when possible ("14:00" vs "odpoledne")

### Issue: Conflicts not detected
- Verify minimum spacing configuration (default: 24 hours)
- Check that meeting times are in ISO format
- Ensure meetings have status='scheduled'

### Issue: AI not detecting meeting requests
- Add more meeting keywords to knowledge base
- Check intent detection in AI engine logs
- Verify meeting scheduler is initialized

## Future Enhancements

Potential improvements for future versions:
- Email notifications
- Calendar sync (Google Calendar, Outlook)
- SMS reminders
- Multiple time zones support
- Recurring meetings
- Meeting notes and follow-up tasks
- Integration with CRM systems

## Support

For issues or questions:
- Check logs in `server.log`
- Review meeting database: `data/meetings.db`
- Test with `/tmp/test_meeting_system.py`
