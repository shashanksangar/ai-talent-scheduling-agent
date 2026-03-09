"""
AI Talent Operations - Scheduling Agent CLI

Interactive command-line interface for the intelligent scheduling system.
Provides menu-driven interface for scheduling interviews with rule enforcement.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from scheduling_agent import SchedulingAgent, InterviewSlot
except ImportError:
    print("❌ Error: Could not import SchedulingAgent. Make sure scheduling_agent.py is in the same directory.")
    sys.exit(1)

console = Console()


class SchedulingCLI:
    """Command-line interface for the Scheduling Agent."""

    def __init__(self):
        """Initialize the CLI with the scheduling agent."""
        try:
            self.agent = SchedulingAgent()
            self.current_menu = "main"
            console.print("[green]✅ Scheduling Agent initialized successfully![/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize Scheduling Agent: {e}[/red]")
            sys.exit(1)

    def run(self):
        """Run the main CLI loop."""
        console.print(Panel.fit(
            "[bold blue]🤖 AI Talent Scheduling Agent[/bold blue]\n"
            "[dim]Intelligent scheduling with thumb rule enforcement[/dim]\n"
            "[yellow]📋 Thumb Rule: Maximum 1 interviewer per week[/yellow]",
            title="Welcome"
        ))

        while True:
            try:
                if self.current_menu == "main":
                    self.show_main_menu()
                elif self.current_menu == "schedule":
                    self.show_schedule_menu()
                elif self.current_menu == "view":
                    self.show_view_menu()
                elif self.current_menu == "reports":
                    self.show_reports_menu()

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                self.current_menu = "main"

    def show_main_menu(self):
        """Display the main menu."""
        console.print("\n[bold cyan]📋 Main Menu[/bold cyan]")

        choices = [
            "📅 Schedule New Interview",
            "👀 View Schedule",
            "📊 Reports & Analytics",
            "🔍 Check Availability",
            "⚙️  Settings",
            "❌ Exit"
        ]

        choice = questionary.select(
            "Select an option:",
            choices=choices,
            pointer="▶"
        ).ask()

        if choice == "📅 Schedule New Interview":
            self.current_menu = "schedule"
        elif choice == "👀 View Schedule":
            self.current_menu = "view"
        elif choice == "📊 Reports & Analytics":
            self.current_menu = "reports"
        elif choice == "🔍 Check Availability":
            self.check_availability()
        elif choice == "⚙️  Settings":
            self.show_settings()
        elif choice == "❌ Exit":
            console.print("[yellow]👋 Goodbye![/yellow]")
            sys.exit(0)

    def show_schedule_menu(self):
        """Display the scheduling menu."""
        console.print("\n[bold cyan]📅 Schedule New Interview[/bold cyan]")

        # Get interviewer
        interviewers = list(self.agent.interviewers.keys())
        interviewer = questionary.select(
            "Select interviewer:",
            choices=interviewers
        ).ask()

        if not interviewer:
            self.current_menu = "main"
            return

        # Get candidate name
        candidate = questionary.text("Candidate name:").ask()
        if not candidate:
            self.current_menu = "main"
            return

        # Get role
        role = questionary.text("Role/Position:").ask()
        if not role:
            self.current_menu = "main"
            return

        # Get date
        date_str = questionary.text(
            "Interview date (YYYY-MM-DD or MM/DD/YYYY):",
            validate=lambda x: self._validate_date(x)
        ).ask()

        if not date_str:
            self.current_menu = "main"
            return

        # Get duration
        duration_choices = ["30", "45", "60", "90", "120"]
        duration = questionary.select(
            "Duration (minutes):",
            choices=duration_choices,
            default="60"
        ).ask()

        # Get notes
        notes = questionary.text("Additional notes (optional):").ask()

        # Validate and schedule
        console.print("\n[bold]🔍 Validating request...[/bold]")

        is_valid, errors = self.agent.validate_interview_request(
            interviewer, candidate, role, date_str
        )

        if not is_valid:
            console.print("[red]❌ Validation failed:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print("\n[yellow]Please correct the issues and try again.[/yellow]")
        else:
            # Schedule the interview
            success, message = self.agent.schedule_interview(
                interviewer, candidate, role, date_str,
                duration=int(duration), notes=notes or ""
            )

            if success:
                console.print(f"[green]{message}[/green]")
                console.print("[green]✅ Interview scheduled and synced with calendar![/green]")
            else:
                console.print(f"[red]❌ Failed to schedule: {message}[/red]")

        # Return to main menu
        input("\nPress Enter to continue...")
        self.current_menu = "main"

    def show_view_menu(self):
        """Display the view schedule menu."""
        console.print("\n[bold cyan]👀 View Schedule[/bold cyan]")

        choices = [
            "📅 View Today's Schedule",
            "📆 View This Week's Schedule",
            "👥 View by Interviewer",
            "🔙 Back to Main Menu"
        ]

        choice = questionary.select(
            "Select view:",
            choices=choices
        ).ask()

        if choice == "📅 View Today's Schedule":
            self.view_today_schedule()
        elif choice == "📆 View This Week's Schedule":
            self.view_week_schedule()
        elif choice == "👥 View by Interviewer":
            self.view_by_interviewer()
        elif choice == "🔙 Back to Main Menu":
            self.current_menu = "main"

    def show_reports_menu(self):
        """Display the reports menu."""
        console.print("\n[bold cyan]📊 Reports & Analytics[/bold cyan]")

        choices = [
            "📈 Schedule Summary",
            "👥 Interviewer Workload",
            "📊 Utilization Report",
            "🔙 Back to Main Menu"
        ]

        choice = questionary.select(
            "Select report:",
            choices=choices
        ).ask()

        if choice == "📈 Schedule Summary":
            self.show_schedule_summary()
        elif choice == "👥 Interviewer Workload":
            self.show_interviewer_workload()
        elif choice == "📊 Utilization Report":
            self.show_utilization_report()
        elif choice == "🔙 Back to Main Menu":
            self.current_menu = "main"

    def check_availability(self):
        """Check interviewer availability for a specific date."""
        console.print("\n[bold cyan]🔍 Check Availability[/bold cyan]")

        date_str = questionary.text(
            "Date to check (YYYY-MM-DD or MM/DD/YYYY):",
            validate=lambda x: self._validate_date(x)
        ).ask()

        if not date_str:
            return

        available = self.agent.get_available_interviewers(date_str)

        if available:
            console.print(f"[green]✅ Available interviewers on {date_str}:[/green]")
            for interviewer in available:
                console.print(f"  • {interviewer}")
        else:
            console.print(f"[red]❌ No interviewers available on {date_str}[/red]")

        input("\nPress Enter to continue...")

    def view_today_schedule(self):
        """View today's scheduled interviews."""
        today = datetime.now().date()
        today_slots = [
            slot for slot in self.agent.scheduled_interviews
            if slot.date.date() == today
        ]

        self._display_schedule_table(today_slots, f"Today's Schedule ({today})")

    def view_week_schedule(self):
        """View this week's scheduled interviews."""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)

        week_slots = [
            slot for slot in self.agent.scheduled_interviews
            if week_start.date() <= slot.date.date() <= week_end.date()
        ]

        week_range = f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d/%Y')}"
        self._display_schedule_table(week_slots, f"This Week's Schedule ({week_range})")

    def view_by_interviewer(self):
        """View schedule by interviewer."""
        interviewer = questionary.select(
            "Select interviewer:",
            choices=list(self.agent.interviewers.keys())
        ).ask()

        if not interviewer:
            return

        interviewer_slots = [
            slot for slot in self.agent.scheduled_interviews
            if slot.interviewer == interviewer
        ]

        self._display_schedule_table(interviewer_slots, f"{interviewer}'s Schedule")

    def _display_schedule_table(self, slots: List[InterviewSlot], title: str):
        """Display a table of interview slots."""
        table = Table(title=title)
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Time", style="magenta", no_wrap=True)
        table.add_column("Interviewer", style="green")
        table.add_column("Candidate", style="yellow")
        table.add_column("Role", style="blue")
        table.add_column("Duration", style="dim", no_wrap=True)
        table.add_column("Notes", style="dim")

        if not slots:
            console.print(f"[dim]No interviews scheduled for {title.lower()}[/dim]")
        else:
            for slot in sorted(slots, key=lambda x: x.date):
                table.add_row(
                    slot.date.strftime("%Y-%m-%d"),
                    slot.date.strftime("%H:%M"),
                    slot.interviewer,
                    slot.candidate,
                    slot.role,
                    f"{slot.duration_minutes}m",
                    slot.notes or ""
                )
            console.print(table)

        input("\nPress Enter to continue...")

    def show_schedule_summary(self):
        """Show overall schedule summary."""
        summary = self.agent.get_schedule_summary()

        console.print("\n[bold cyan]📈 Schedule Summary[/bold cyan]")
        console.print(f"Total Interviewers: {summary['total_interviewers']}")
        console.print(f"Scheduled Interviews: {summary['scheduled_interviews']}")

        # Interviewer availability table
        table = Table(title="Interviewer Availability")
        table.add_column("Interviewer", style="green")
        table.add_column("This Week", style="yellow", no_wrap=True)
        table.add_column("Available", style="cyan", no_wrap=True)
        table.add_column("Last Interview", style="dim")

        for name, data in summary['interviewer_availability'].items():
            available = "✅ Yes" if data['can_schedule_this_week'] else "❌ No"
            last_interview = data['last_interview'] or "None"
            if last_interview != "None":
                last_interview = datetime.fromisoformat(last_interview).strftime("%m/%d")

            table.add_row(
                name,
                str(data['interviews_this_week']),
                available,
                last_interview
            )

        console.print(table)
        input("\nPress Enter to continue...")

    def show_interviewer_workload(self):
        """Show interviewer workload report."""
        console.print("\n[bold cyan]👥 Interviewer Workload[/bold cyan]")

        # Group interviews by interviewer
        workload = {}
        for slot in self.agent.scheduled_interviews:
            if slot.interviewer not in workload:
                workload[slot.interviewer] = []
            workload[slot.interviewer].append(slot)

        table = Table(title="Interviewer Workload")
        table.add_column("Interviewer", style="green")
        table.add_column("Total Interviews", style="yellow", no_wrap=True)
        table.add_column("This Week", style="cyan", no_wrap=True)
        table.add_column("Next Interview", style="magenta")

        for interviewer_name in self.agent.interviewers.keys():
            interviews = workload.get(interviewer_name, [])
            this_week = sum(1 for slot in interviews
                          if self._is_this_week(slot.date))

            next_interview = None
            future_interviews = [slot for slot in interviews if slot.date > datetime.now()]
            if future_interviews:
                next_interview = min(future_interviews, key=lambda x: x.date)
                next_interview = next_interview.date.strftime("%m/%d %H:%M")

            table.add_row(
                interviewer_name,
                str(len(interviews)),
                str(this_week),
                next_interview or "None"
            )

        console.print(table)
        input("\nPress Enter to continue...")

    def show_utilization_report(self):
        """Show utilization analytics."""
        console.print("\n[bold cyan]📊 Utilization Report[/bold cyan]")

        total_interviewers = len(self.agent.interviewers)
        scheduled_this_week = sum(
            1 for slot in self.agent.scheduled_interviews
            if self._is_this_week(slot.date)
        )

        max_possible = total_interviewers  # 1 per interviewer per week
        utilization_rate = (scheduled_this_week / max_possible * 100) if max_possible > 0 else 0

        console.print(f"Scheduled this week: {scheduled_this_week}")
        console.print(f"Maximum capacity: {max_possible}")
        console.print(".1f"
        # Show utilization by day
        now = datetime.now()
        week_days = []
        for i in range(7):
            day = now + timedelta(days=i)
            day_slots = [
                slot for slot in self.agent.scheduled_interviews
                if slot.date.date() == day.date()
            ]
            week_days.append((day.strftime("%a %m/%d"), len(day_slots)))

        table = Table(title="Daily Utilization (This Week)")
        table.add_column("Day", style="cyan")
        table.add_column("Interviews", style="yellow")

        for day, count in week_days:
            table.add_row(day, str(count))

        console.print(table)
        input("\nPress Enter to continue...")

    def show_settings(self):
        """Show settings menu."""
        console.print("\n[bold cyan]⚙️ Settings[/bold cyan]")
        console.print("[dim]Settings functionality coming soon...[/dim]")
        input("\nPress Enter to continue...")

    def _validate_date(self, date_str: str) -> bool:
        """Validate date string format."""
        try:
            self.agent._parse_date(date_str)
            return True
        except ValueError:
            return False

    def _is_this_week(self, date: datetime) -> bool:
        """Check if date is in current week."""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start.date() <= date.date() <= week_end.date()


def main():
    """Main entry point."""
    try:
        cli = SchedulingCLI()
        cli.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
