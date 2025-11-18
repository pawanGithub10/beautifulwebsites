# Lead Service

**Port:** 8013  
**Purpose:** Lead capture and management for businesses

Complete lead management system for capturing, tracking, and converting leads.

## Features

- **Lead Forms**: Configurable lead capture forms
- **Lead Management**: Complete lead lifecycle tracking
- **Lead Scoring**: Automatic lead scoring based on criteria
- **Notes & Activities**: Track interactions and follow-ups
- **Status Workflow**: new → contacted → qualified → converted → lost
- **Multi-site Support**: Complete tenant isolation

## Database Schema

**4 Tables:**
- lead_forms: Configurable forms for different purposes
- leads: Captured leads with contact information
- lead_notes: Notes and comments on leads
- lead_activities: Activity tracking (calls, emails, meetings)

## API Endpoints

**Forms:** CRUD for lead capture forms
**Leads:** Lead management with status tracking
**Notes:** Add notes and comments
**Activities:** Track follow-up activities

## Quick Start

```bash
pip install -r requirements.txt
python -m app.main
# Visit http://localhost:8013/docs
```

## Key Features

✅ Configurable lead forms
✅ Lead status workflow
✅ Lead scoring
✅ Activity tracking
✅ Notes and comments
✅ Event-driven notifications
✅ Multi-site support

**Version:** 1.0.0
