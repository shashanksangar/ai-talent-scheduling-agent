# AI Talent Scheduling Agent

A specialized AI agent for intelligent interview scheduling with built-in thumb rules and conflict prevention.

## 🎯 Purpose

The Scheduling Agent addresses common recruiting operational inefficiencies:

- **Data Entry Errors**: Prevents manual Excel input mistakes through validation
- **Over-scheduling**: Enforces "1 interviewer per week" thumb rule
- **Calendar Conflicts**: Integrates with Outlook to check availability
- **Process Inefficiency**: Automates scheduling workflow with intelligent recommendations

## ✨ Features

### Core Functionality
- ✅ **Thumb Rule Enforcement**: Maximum 1 interview per interviewer per week
- ✅ **Data Validation**: Prevents common input errors and conflicts
- ✅ **Calendar Integration**: Outlook calendar sync (framework ready)
- ✅ **Availability Tracking**: Real-time interviewer availability checking
- ✅ **Conflict Detection**: Automatic detection of scheduling conflicts

### User Interface
- 🖥️ **Interactive CLI**: Menu-driven interface with rich formatting
- 📊 **Reports & Analytics**: Workload and utilization reporting
- 🔍 **Schedule Views**: Multiple viewing options (daily, weekly, by interviewer)

### Integration Ready
- 🔗 **Outlook Calendar**: Framework for Microsoft Graph API integration
- 🤖 **Agent Orchestration**: Works with Sourcing, Matching, and Outreach agents

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python scheduling_cli.py

# Or use programmatically
from scheduling_agent import SchedulingAgent

agent = SchedulingAgent()
result = agent.schedule_interview(
    interviewer_name="Sarah Chen",
    candidate="John Doe",
    role="ML Engineer",
    date_str="2026-03-15"
)
```

## 📋 Usage Examples

### CLI Interface
```bash
# Interactive scheduling
python scheduling_cli.py

# Direct scheduling
python scheduling_cli.py --interviewer "Sarah Chen" --candidate "John Doe" --role "ML Engineer" --date "2026-03-15"
```

### Demo Script
```bash
python demo_scheduling.py
```

## 🏗️ Architecture

- `scheduling_agent.py` - Core scheduling logic and business rules
- `scheduling_cli.py` - Command-line interface with rich formatting
- `scheduling_config.yaml` - Configuration and interviewer data
- `test_scheduling.py` - Comprehensive test suite

## 🔧 Configuration

Edit `scheduling_config.yaml` to:
- Add/remove interviewers
- Configure availability rules
- Set up calendar integrations
- Customize validation rules

## 🧪 Testing

```bash
# Run all tests
python -m pytest test_scheduling.py -v

# Run with coverage
python -m pytest test_scheduling.py --cov=scheduling_agent
```

## 🤝 Integration

This agent integrates with the main [AI Talent Operations](https://github.com/shashanksangar/ai-talent-operations) orchestrator.

## 📄 License

MIT License
- 📧 **Notifications**: Email and Slack notification support (configurable)

## 🚀 Quick Start

### Prerequisites
```bash
pip install questionary rich pyyaml
```

### Basic Usage
```python
from scheduling_agent import SchedulingAgent

# Initialize agent
agent = SchedulingAgent()

# Check availability
available = agent.get_available_interviewers("2024-01-15")
print(f"Available interviewers: {available}")

# Schedule interview
success, message = agent.schedule_interview(
    interviewer_name="Sarah Chen",
    candidate="John Doe",
    role="Senior Engineer",
    date_str="2024-01-15"
)
print(message)
```

### CLI Interface
```bash
python scheduling_cli.py
```

## 📋 Menu Options

### Main Menu
- 📅 **Schedule New Interview**: Interactive scheduling with validation
- 👀 **View Schedule**: Multiple viewing options
- 📊 **Reports & Analytics**: Workload and utilization reports
- 🔍 **Check Availability**: Quick availability lookup
- ⚙️ **Settings**: Configuration management

### Scheduling Process
1. Select interviewer from available list
2. Enter candidate name and role
3. Specify date (multiple formats supported)
4. Choose duration (30-120 minutes)
5. Add optional notes
6. Automatic validation and conflict checking
7. Schedule confirmation with calendar sync

## 🔧 Configuration

### Basic Settings
```yaml
scheduling:
  max_interviews_per_week: 1
  business_hours:
    start: "09:00"
    end: "17:00"
```

### Calendar Integration
```yaml
calendar:
  provider: "outlook"
  outlook:
    client_id: "${OUTLOOK_CLIENT_ID}"
    tenant_id: "${OUTLOOK_TENANT_ID}"
```

### Validation Rules
```yaml
validation:
  enforce_thumb_rules: true
  check_calendar_conflicts: true
  allow_weekend_scheduling: false
```

## 📊 Reports & Analytics

### Schedule Summary
- Total interviewers and scheduled interviews
- Current week utilization
- Interviewer availability status

### Workload Report
- Interviews per interviewer
- Weekly distribution
- Upcoming interview schedule

### Utilization Analytics
- Weekly capacity utilization percentage
- Daily breakdown
- Trend analysis

## 🔗 Integration Points

### With Other Agents
- **Sourcing Agent**: Candidate pipeline data
- **Matching Agent**: Interview priority scoring
- **Outreach Agent**: Automated scheduling confirmations

### Calendar Systems
- **Outlook**: Primary calendar integration (Microsoft Graph API)
- **Google Calendar**: Future support planned
- **Custom Calendars**: Extensible provider system

## 🛠️ Development

### Project Structure
```
workflows/scheduling/
├── scheduling_agent.py      # Core scheduling logic
├── scheduling_cli.py        # Command-line interface
├── scheduling_config.yaml   # Configuration file
├── schedule.json           # Schedule data storage
└── README.md              # This file
```

### Key Classes

#### SchedulingAgent
Main scheduling engine with rule enforcement and validation.

#### Interviewer
Represents interviewer with availability tracking.

#### InterviewSlot
Data structure for scheduled interview slots.

#### SchedulingCLI
Rich console interface with menu system.

## 🔒 Security & Compliance

- **Data Validation**: Comprehensive input sanitization
- **Audit Trail**: All scheduling actions logged
- **Access Control**: Interviewer-specific permissions (planned)
- **GDPR Compliance**: Data minimization and consent management

## 📈 Future Enhancements

### Planned Features
- [ ] **Microsoft Graph API**: Full Outlook calendar integration
- [ ] **Automated Reminders**: Email/Slack notifications
- [ ] **Bulk Scheduling**: CSV import for multiple interviews
- [ ] **Analytics Dashboard**: Web-based reporting interface
- [ ] **Mobile App**: iOS/Android scheduling companion
- [ ] **AI Recommendations**: ML-powered interviewer matching

### Integration Expansions
- [ ] **Zoom/Teams Integration**: Automatic meeting creation
- [ ] **HRIS Systems**: Employee data synchronization
- [ ] **ATS Integration**: Applicant tracking system sync
- [ ] **Video Interview Platforms**: Automated setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all validation passes
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check the [troubleshooting guide](#troubleshooting)
- Review [configuration examples](#configuration)
- Open an issue on GitHub

## 📋 Troubleshooting

### Common Issues

**"Interviewer not available"**
- Check thumb rule compliance (max 1 per week)
- Verify calendar conflicts
- Confirm interviewer exists in system

**"Invalid date format"**
- Use YYYY-MM-DD or MM/DD/YYYY
- Ensure date is not in the past

**"Calendar sync failed"**
- Verify Outlook credentials in config
- Check network connectivity
- Confirm calendar permissions

### Debug Mode
```bash
export SCHEDULING_DEBUG=true
python scheduling_cli.py
```

## 📄 License

This project is part of the AI Talent Copilot ecosystem. See main project license for details.
