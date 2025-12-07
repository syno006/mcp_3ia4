import os
import sys
sys.path.insert(0, r'C:\Users\Yassine\OneDrive\Bureau\python framework\GestionConference')  # Add this line
import django
from mcp.server.fastmcp import FastMCP
from asgiref.sync import sync_to_async
from datetime import date

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GestionConference.settings")
django.setup()

# Import models after Django setup
from ConferenceApp.models import Conference
from SessionApp.models import Session

# Create the MCP server
mcp = FastMCP("Conference Assistant")

@mcp.tool()
async def list_conferences() -> str:
    """List all available conferences."""
    @sync_to_async
    def _get_conferences():
        return list(Conference.objects.all())
    
    conferences = await _get_conferences()
    if not conferences:
        return "No conferences found."
    return "\n".join([f"- {c.name} ({c.start_date} to {c.end_date})" for c in conferences])

@mcp.tool()
async def get_conference_details(name: str) -> str:
    """Get details of a specific conference by name."""
    @sync_to_async
    def _get_conference():
        try:
            return Conference.objects.get(name__icontains=name)
        except Conference.DoesNotExist:
            return None
        except Conference.MultipleObjectsReturned:
            return "MULTIPLE"
    
    conference = await _get_conference()
    if conference == "MULTIPLE":
        return f"Multiple conferences found matching '{name}'. Please be more specific."
    if not conference:
        return f"Conference '{name}' not found."
    
    return (
        f"Name: {conference.name}\n"
        f"Theme: {conference.get_theme_display()}\n"
        f"Location: {conference.location}\n"
        f"Dates: {conference.start_date} to {conference.end_date}\n"
        f"Description: {conference.description}"
    )

@mcp.tool()
async def list_sessions(conference_name: str) -> str:
    """List sessions for a specific conference."""
    @sync_to_async
    def _get_sessions():
        try:
            conference = Conference.objects.get(name__icontains=conference_name)
            return list(conference.sessions.all()), conference
        except Conference.DoesNotExist:
            return None, None
        except Conference.MultipleObjectsReturned:
            return "MULTIPLE", None
    
    result, conference = await _get_sessions()
    if result == "MULTIPLE":
        return f"Multiple conferences found matching '{conference_name}'. Please be more specific."
    if conference is None:
        return f"Conference '{conference_name}' not found."
    
    sessions = result
    if not sessions:
        return f"No sessions found for conference '{conference.name}'."
    
    session_list = []
    for s in sessions:
        session_list.append(
            f"- {s.title} ({s.start_time} - {s.end_time}) in {s.room}\n"
            f"  Topic: {s.topic}"
        )
    return "\n".join(session_list)

@mcp.tool()
async def filter_conferences_by_start_date(start_date: str) -> str:
    """List conferences starting after the given date (format: YYYY-MM-DD)."""
    try:
        d = date.fromisoformat(start_date)
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."
    
    @sync_to_async
    def _get_conferences():
        return list(Conference.objects.filter(start_date__gt=d))
    
    conferences = await _get_conferences()
    if not conferences:
        return "No conferences found starting after that date."
    return "\n".join([f"- {c.name} ({c.start_date} to {c.end_date})" for c in conferences])

if __name__ == "__main__":
    mcp.run(transport="stdio")