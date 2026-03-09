"""
AI Talent Operations - Scheduling Agent Tests

Basic tests to validate scheduling agent functionality.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scheduling_agent import SchedulingAgent, Interviewer, InterviewSlot


class TestSchedulingAgent(unittest.TestCase):
    """Test cases for SchedulingAgent."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write("""
scheduling:
  max_interviews_per_week: 1
""")
        self.temp_config.close()

        # Create agent with temp config
        self.agent = SchedulingAgent(self.temp_config.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
        # Clean up any created schedule files
        if os.path.exists("schedule.json"):
            os.unlink("schedule.json")

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsInstance(self.agent, SchedulingAgent)
        self.assertGreater(len(self.agent.interviewers), 0)
        self.assertIsInstance(self.agent.scheduled_interviews, list)

    def test_interviewer_creation(self):
        """Test interviewer objects are created properly."""
        interviewer = self.agent.interviewers["Sarah Chen"]
        self.assertEqual(interviewer.name, "Sarah Chen")
        self.assertEqual(interviewer.email, "sarah.chen@company.com")
        self.assertEqual(interviewer.interviews_this_week, 0)

    def test_date_parsing(self):
        """Test date parsing with different formats."""
        # Test YYYY-MM-DD
        date1 = self.agent._parse_date("2024-01-15")
        self.assertEqual(date1.strftime("%Y-%m-%d"), "2024-01-15")

        # Test MM/DD/YYYY
        date2 = self.agent._parse_date("01/15/2024")
        self.assertEqual(date2.strftime("%Y-%m-%d"), "2024-01-15")

        # Test invalid date
        with self.assertRaises(ValueError):
            self.agent._parse_date("invalid-date")

    def test_availability_check(self):
        """Test interviewer availability checking."""
        interviewer = self.agent.interviewers["Sarah Chen"]

        # Should be available initially
        future_date = datetime.now() + timedelta(days=8)  # Monday
        self.assertTrue(interviewer.can_schedule_this_week(future_date))

        # Schedule an interview
        self.assertTrue(interviewer.schedule_interview(future_date))
        self.assertEqual(interviewer.interviews_this_week, 1)

        # Should not be available for same week
        same_week_date = future_date + timedelta(days=1)  # Tuesday, same week
        self.assertFalse(interviewer.can_schedule_this_week(same_week_date))

    def test_validation(self):
        """Test interview request validation."""
        # Valid request with future date
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        is_valid, errors = self.agent.validate_interview_request(
            "Sarah Chen", "John Doe", "Senior Engineer", future_date
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid interviewer
        is_valid, errors = self.agent.validate_interview_request(
            "Invalid Name", "John Doe", "Senior Engineer", future_date
        )
        self.assertFalse(is_valid)
        self.assertIn("not found", errors[0])

        # Past date
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        is_valid, errors = self.agent.validate_interview_request(
            "Sarah Chen", "John Doe", "Senior Engineer", past_date
        )
        self.assertFalse(is_valid)
        self.assertIn("past", errors[0])

    def test_scheduling(self):
        """Test interview scheduling."""
        # Schedule a valid interview with future date
        future_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")  # Monday
        success, message = self.agent.schedule_interview(
            "Sarah Chen", "John Doe", "Senior Engineer", future_date
        )

        self.assertTrue(success)
        self.assertIn("scheduled", message)
        self.assertEqual(len(self.agent.scheduled_interviews), 1)

        # Check interviewer was updated
        interviewer = self.agent.interviewers["Sarah Chen"]
        self.assertEqual(interviewer.interviews_this_week, 1)

        # Try to schedule another interview same week (should fail)
        same_week_date = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")  # Tuesday, same week
        success, message = self.agent.schedule_interview(
            "Sarah Chen", "Jane Smith", "Product Manager", same_week_date
        )

        self.assertFalse(success)
        self.assertIn("thumb rule", message)

    def test_schedule_summary(self):
        """Test schedule summary generation."""
        summary = self.agent.get_schedule_summary()

        self.assertIn("total_interviewers", summary)
        self.assertIn("scheduled_interviews", summary)
        self.assertIn("interviewer_availability", summary)

        # Check interviewer data structure
        availability = summary["interviewer_availability"]["Sarah Chen"]
        self.assertIn("interviews_this_week", availability)
        self.assertIn("can_schedule_this_week", availability)

    def test_available_interviewers(self):
        """Test getting available interviewers."""
        # Initially all should be available
        future_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")  # Monday
        available = self.agent.get_available_interviewers(future_date)
        self.assertGreater(len(available), 0)

        # Schedule one interviewer
        self.agent.schedule_interview(
            "Sarah Chen", "John Doe", "Senior Engineer", future_date
        )

        # Sarah should not be available for same week
        same_week = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")  # Tuesday, same week
        available = self.agent.get_available_interviewers(same_week)
        self.assertNotIn("Sarah Chen", available)


class TestInterviewer(unittest.TestCase):
    """Test cases for Interviewer class."""

    def test_interviewer_initialization(self):
        """Test interviewer initialization."""
        interviewer = Interviewer(
            name="Test User",
            email="test@example.com",
            role="Test Role"
        )

        self.assertEqual(interviewer.name, "Test User")
        self.assertEqual(interviewer.interviews_this_week, 0)
        self.assertIsNone(interviewer.last_interview_date)

    def test_availability_logic(self):
        """Test interviewer availability logic."""
        interviewer = Interviewer("Test", "test@test.com", "Role")

        # Initially available
        future_date = datetime.now() + timedelta(days=8)  # Monday
        self.assertTrue(interviewer.can_schedule_this_week(future_date))

        # After scheduling
        interviewer.schedule_interview(future_date)
        self.assertEqual(interviewer.interviews_this_week, 1)
        self.assertFalse(interviewer.can_schedule_this_week(future_date))

        # Different week should be available
        next_week = future_date + timedelta(days=7)  # Next Monday
        self.assertTrue(interviewer.can_schedule_this_week(next_week))


class TestInterviewSlot(unittest.TestCase):
    """Test cases for InterviewSlot class."""

    def test_slot_creation(self):
        """Test interview slot creation."""
        date = datetime(2024, 1, 15, 10, 0)
        slot = InterviewSlot(
            interviewer="Sarah Chen",
            candidate="John Doe",
            role="Senior Engineer",
            date=date,
            duration_minutes=60,
            notes="Technical interview"
        )

        self.assertEqual(slot.interviewer, "Sarah Chen")
        self.assertEqual(slot.candidate, "John Doe")
        self.assertEqual(slot.duration_minutes, 60)

    def test_slot_to_dict(self):
        """Test slot serialization."""
        date = datetime(2024, 1, 15, 10, 0)
        slot = InterviewSlot(
            interviewer="Sarah Chen",
            candidate="John Doe",
            role="Senior Engineer",
            date=date
        )

        data = slot.to_dict()
        self.assertEqual(data["interviewer"], "Sarah Chen")
        self.assertEqual(data["candidate"], "John Doe")
        self.assertEqual(data["date"], date.isoformat())


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
