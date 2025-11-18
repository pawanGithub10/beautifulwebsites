# Booking Service

**Port:** 8012  
**Purpose:** Appointment and booking management for service-based businesses

Complete booking system for salons, coaching centers, consultancies, and any time-based service businesses.

## Features

- **Service Catalog**: Services and categories with flexible pricing
- **Provider Management**: Staff/professionals with scheduling
- **Availability**: Smart slot calculation with recurring and override schedules
- **Bookings**: Complete appointment lifecycle management
- **Cancellation**: Policy-based cancellation with fees
- **Multi-site Support**: Complete tenant isolation

## Database Schema

**8 Tables:**
- service_categories: Hierarchical service categories
- services: Service offerings with duration and pricing
- providers: Staff members with skills
- recurring_schedules: Weekly availability patterns
- provider_schedules: Specific date overrides
- blocked_slots: Holidays, breaks, unavailable times
- bookings: Appointments with customer details
- booking_history: Complete audit trail

## API Endpoints

**Services:** 10+ endpoints for catalog management
**Providers:** 8+ endpoints for provider/schedule management
**Availability:** Real-time slot checking
**Bookings:** 8+ endpoints for booking lifecycle

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m app.main

# API docs
http://localhost:8012/docs
```

## Key Features

✅ Smart availability calculation
✅ Double-booking prevention
✅ Recurring weekly schedules
✅ Specific date overrides
✅ Site-wide and provider-specific blocks
✅ Cancellation policies
✅ Booking history audit trail
✅ Multi-provider support

**Version:** 1.0.0
**Lines of Code:** ~3,000+
