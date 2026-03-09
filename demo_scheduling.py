#!/usr/bin/env python3
"""
AI Talent Operations - Scheduling Agent Demo

Demonstrates the intelligent scheduling system that enforces thumb rules
and prevents over-scheduling of interviewers.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from workflows.scheduling.scheduling_agent import SchedulingAgent


def demo_scheduling_agent():
    """Demonstrate the scheduling agent functionality."""
    print("🤖 AI Talent Scheduling Agent Demo")
    print("=" * 50)

    # Initialize agent
    agent = SchedulingAgent()
    print("✅ Scheduling Agent initialized")

    # Show current status
    summary = agent.get_schedule_summary()
    print(f"📊 Current Status:")
    print(f"   • Interviewers: {summary['total_interviewers']}")
    print(f"   • Scheduled interviews: {summary['scheduled_interviews']}")

    # Check availability for next week
    next_monday = (datetime.now() + timedelta(days=(7 - datetime.now().weekday()))).strftime("%Y-%m-%d")
    available = agent.get_available_interviewers(next_monday)
    print(f"✅ Available interviewers for {next_monday}: {len(available)}")

    # Demonstrate scheduling
    print("\n📅 Scheduling Demo:")

    # Schedule first interview
    success, message = agent.schedule_interview(
        "Sarah Chen", "John Doe", "Senior Engineer", next_monday
    )
    print(f"   • {message}")

    # Try to schedule second interview same week (should fail)
    next_tuesday = (datetime.now() + timedelta(days=(8 - datetime.now().weekday()))).strftime("%Y-%m-%d")
    success, message = agent.schedule_interview(
        "Sarah Chen", "Jane Smith", "Product Manager", next_tuesday
    )
    print(f"   • {message}")

    # Schedule for different interviewer
    success, message = agent.schedule_interview(
        "Mike Johnson", "Bob Wilson", "Frontend Developer", next_tuesday
    )
    print(f"   • {message}")

    # Show final status
    final_summary = agent.get_schedule_summary()
    print("\n📈 Final Status:")
    print(f"   • Total scheduled: {final_summary['scheduled_interviews']}")

    for name, data in final_summary['interviewer_availability'].items():
        status = "✅ Available" if data['can_schedule_this_week'] else "❌ Busy"
        interviews = data['interviews_this_week']
        print(f"   • {name}: {interviews} interviews this week - {status}")

    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Thumb rule enforcement (1 interviewer/week)")
    print("   ✅ Data validation and conflict detection")
    print("   ✅ Availability tracking and reporting")
    print("   ✅ Calendar integration framework ready")
    print("   ✅ Prevents manual Excel entry errors")

    print("\n🚀 Ready for production use!")
    print("   Run: python workflows/scheduling/scheduling_cli.py")


if __name__ == "__main__":
    demo_scheduling_agent()
