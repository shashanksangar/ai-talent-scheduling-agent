"""
AI Talent Operations - Scheduling Agent

Intelligent scheduling system that enforces thumb rules and prevents over-scheduling.
Enforces: 1 interviewer per week maximum
Integrates with: Outlook calendar
Validates: Data entry to prevent errors
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Interviewer:
    """Represents an interviewer with availability tracking."""
    name: str
    email: str
    role: str
    interviews_this_week: int = 0
    last_interview_date: Optional[datetime] = None
    availability_notes: str = ""

    def can_schedule_this_week(self, check_date: datetime) -> bool:
        """Check if interviewer can be scheduled this week."""
        # If no previous interviews, they're available
        if not self.last_interview_date:
            return True

        # Check if the check_date is in the same week as last interview
        check_week_start = check_date - timedelta(days=check_date.weekday())
        last_week_start = self.last_interview_date - timedelta(days=self.last_interview_date.weekday())

        # If same week and already has interview, not available
        if check_week_start == last_week_start and self.interviews_this_week >= 1:
            return False

        # If different week, available (reset would happen when scheduling)
        return True

    def schedule_interview(self, interview_date: datetime) -> bool:
        """Schedule an interview for this interviewer."""
        if not self.can_schedule_this_week(interview_date):
            return False

        # Check if this is a different week from last interview
        if self.last_interview_date:
            current_week_start = interview_date - timedelta(days=interview_date.weekday())
            last_week_start = self.last_interview_date - timedelta(days=self.last_interview_date.weekday())

            # If different week, reset counter
            if current_week_start != last_week_start:
                self.interviews_this_week = 0

        self.interviews_this_week += 1
        self.last_interview_date = interview_date
        return True


@dataclass
class InterviewSlot:
    """Represents a scheduled interview slot."""
    interviewer: str
    candidate: str
    role: str
    date: datetime
    duration_minutes: int = 60
    meeting_link: str = ""
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "interviewer": self.interviewer,
            "candidate": self.candidate,
            "role": self.role,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "meeting_link": self.meeting_link,
            "notes": self.notes
        }


class SchedulingAgent:
    """
    AI-powered scheduling agent that enforces business rules and integrates with calendars.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Scheduling Agent.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.interviewers: Dict[str, Interviewer] = {}
        self.scheduled_interviews: List[InterviewSlot] = []
        self.validation_errors: List[str] = []

        # Load existing data
        self._load_interviewers()
        self._load_schedule()

        logger.info("Scheduling Agent initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}, using defaults")
            return {}

    def _load_interviewers(self):
        """Load interviewer data from configuration or external source."""
        # In a real implementation, this would load from HR system or database
        # For now, using sample data based on common recruiting team structure

        sample_interviewers = [
            {"name": "Sarah Chen", "email": "sarah.chen@company.com", "role": "Engineering Manager"},
            {"name": "Mike Johnson", "email": "mike.johnson@company.com", "role": "Senior Engineer"},
            {"name": "Lisa Rodriguez", "email": "lisa.rodriguez@company.com", "role": "Product Manager"},
            {"name": "David Kim", "email": "david.kim@company.com", "role": "Tech Lead"},
            {"name": "Anna Patel", "email": "anna.patel@company.com", "role": "HR Business Partner"},
        ]

        for interviewer_data in sample_interviewers:
            interviewer = Interviewer(**interviewer_data)
            self.interviewers[interviewer.name] = interviewer

        logger.info(f"Loaded {len(self.interviewers)} interviewers")

    def _load_schedule(self):
        """Load existing schedule from file or database."""
        schedule_file = "schedule.json"
        if os.path.exists(schedule_file):
            try:
                with open(schedule_file, 'r') as f:
                    data = json.load(f)
                    for slot_data in data.get('scheduled_interviews', []):
                        slot_data['date'] = datetime.fromisoformat(slot_data['date'])
                        slot = InterviewSlot(**slot_data)
                        self.scheduled_interviews.append(slot)

                        # Update interviewer availability
                        if slot.interviewer in self.interviewers:
                            interviewer = self.interviewers[slot.interviewer]
                            interviewer.schedule_interview(slot.date)

                logger.info(f"Loaded {len(self.scheduled_interviews)} scheduled interviews")
            except Exception as e:
                logger.error(f"Error loading schedule: {e}")

    def validate_interview_request(self, interviewer_name: str, candidate: str,
                                 role: str, date_str: str) -> Tuple[bool, List[str]]:
        """
        Validate an interview scheduling request.

        Args:
            interviewer_name: Name of the interviewer
            candidate: Candidate name
            role: Role being interviewed for
            date_str: Date string (YYYY-MM-DD or MM/DD/YYYY)

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate interviewer exists
        if interviewer_name not in self.interviewers:
            errors.append(f"Interviewer '{interviewer_name}' not found. Available: {list(self.interviewers.keys())}")

        # Validate required fields
        if not candidate.strip():
            errors.append("Candidate name is required")
        if not role.strip():
            errors.append("Role is required")

        # Validate date format
        try:
            interview_date = self._parse_date(date_str)
            if interview_date < datetime.now():
                errors.append("Interview date cannot be in the past")
        except ValueError as e:
            errors.append(f"Invalid date format: {e}")

        # Check thumb rule (1 interviewer per week)
        if interviewer_name in self.interviewers and 'interview_date' in locals():
            interviewer = self.interviewers[interviewer_name]
            if not interviewer.can_schedule_this_week(interview_date):
                errors.append(f"Interviewer '{interviewer_name}' already has an interview this week (thumb rule: max 1 per week)")

        # Check for conflicts
        if interviewer_name in self.interviewers and 'interview_date' in locals():
            conflicts = self._check_calendar_conflicts(interviewer_name, interview_date)
            if conflicts:
                errors.append(f"Calendar conflict detected: {conflicts}")

        return len(errors) == 0, errors

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime object."""
        # Try multiple common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%Y/%m/%d"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse date '{date_str}'. Try YYYY-MM-DD or MM/DD/YYYY")

    def _check_calendar_conflicts(self, interviewer_name: str, check_date: datetime) -> str:
        """
        Check for calendar conflicts (placeholder for Outlook integration).

        In a real implementation, this would query Outlook calendar API.
        """
        # Placeholder logic - check against existing schedule
        for slot in self.scheduled_interviews:
            if (slot.interviewer == interviewer_name and
                slot.date.date() == check_date.date()):
                return f"Already scheduled for {slot.candidate} at {slot.date.strftime('%H:%M')}"

        return ""

    def schedule_interview(self, interviewer_name: str, candidate: str,
                          role: str, date_str: str, duration: int = 60,
                          notes: str = "") -> Tuple[bool, str]:
        """
        Schedule a new interview.

        Args:
            interviewer_name: Name of interviewer
            candidate: Candidate name
            role: Role being interviewed for
            date_str: Interview date
            duration: Duration in minutes
            notes: Additional notes

        Returns:
            Tuple of (success, message)
        """
        # Validate request
        is_valid, errors = self.validate_interview_request(
            interviewer_name, candidate, role, date_str
        )

        if not is_valid:
            return False, f"Validation failed: {'; '.join(errors)}"

        try:
            interview_date = self._parse_date(date_str)

            # Create interview slot
            slot = InterviewSlot(
                interviewer=interviewer_name,
                candidate=candidate,
                role=role,
                date=interview_date,
                duration_minutes=duration,
                notes=notes
            )

            # Update interviewer availability
            interviewer = self.interviewers[interviewer_name]
            if not interviewer.schedule_interview(interview_date):
                return False, "Failed to schedule: interviewer unavailable"

            # Add to schedule
            self.scheduled_interviews.append(slot)

            # Save to file
            self._save_schedule()

            # Sync with calendar (placeholder)
            self._sync_with_calendar(slot)

            message = f"✅ Interview scheduled: {candidate} with {interviewer_name} on {interview_date.strftime('%Y-%m-%d')}"
            logger.info(message)
            return True, message

        except Exception as e:
            error_msg = f"Failed to schedule interview: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_available_interviewers(self, date_str: str) -> List[str]:
        """
        Get list of available interviewers for a given date.

        Args:
            date_str: Date to check availability for

        Returns:
            List of available interviewer names
        """
        try:
            check_date = self._parse_date(date_str)
            available = []

            for name, interviewer in self.interviewers.items():
                if interviewer.can_schedule_this_week(check_date):
                    available.append(name)

            return available

        except ValueError as e:
            logger.error(f"Invalid date for availability check: {e}")
            return []

    def get_schedule_summary(self) -> Dict:
        """Get summary of current schedule and availability."""
        summary = {
            "total_interviewers": len(self.interviewers),
            "scheduled_interviews": len(self.scheduled_interviews),
            "interviewer_availability": {}
        }

        for name, interviewer in self.interviewers.items():
            summary["interviewer_availability"][name] = {
                "interviews_this_week": interviewer.interviews_this_week,
                "can_schedule_this_week": interviewer.can_schedule_this_week(datetime.now()),
                "last_interview": interviewer.last_interview_date.isoformat() if interviewer.last_interview_date else None
            }

        return summary

    def _save_schedule(self):
        """Save schedule to JSON file."""
        try:
            data = {
                "scheduled_interviews": [slot.to_dict() for slot in self.scheduled_interviews],
                "last_updated": datetime.now().isoformat()
            }

            with open("schedule.json", 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("Schedule saved to schedule.json")

        except Exception as e:
            logger.error(f"Failed to save schedule: {e}")

    def _sync_with_calendar(self, slot: InterviewSlot):
        """
        Sync interview with Outlook calendar (placeholder).

        In a real implementation, this would use Microsoft Graph API.
        """
        logger.info(f"Calendar sync placeholder: {slot.interviewer} - {slot.candidate} on {slot.date}")


def main():
    """Main entry point for scheduling agent."""
    agent = SchedulingAgent()

    # Example usage
    print("🤖 AI Talent Scheduling Agent")
    print("=" * 40)

    # Show current status
    summary = agent.get_schedule_summary()
    print(f"📊 Status: {summary['scheduled_interviews']} interviews scheduled")
    print(f"👥 Interviewers: {summary['total_interviewers']} total")

    # Show available interviewers for today
    today = datetime.now().strftime("%Y-%m-%d")
    available = agent.get_available_interviewers(today)
    print(f"✅ Available today ({today}): {len(available)} interviewers")

    print("\nReady for scheduling commands!")


if __name__ == "__main__":
    main()
