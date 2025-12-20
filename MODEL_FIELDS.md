# Model Field Lists

## Customer Model
**File:** `models/customer.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique customer identifier |
| `name` | String(100) | Not Null | Customer's name (e.g., "Bamboo Bear", "Forest Fox") |
| `species` | String(50) | Not Null | Animal species (e.g., "Bear", "Fox", "Deer", "Rabbit") |
| `contact_info` | String(200) | Nullable | Contact information (phone, email, or forest location) |
| `created_at` | DateTime | Not Null, Default=now | Account creation timestamp |
| `last_visit` | DateTime | Nullable | Date of last spa visit |
| `total_visits` | Integer | Default=0 | Total number of appointments |
| `total_spent` | Float | Default=0.0 | Cumulative amount spent at spa |
| `notes` | Text | Nullable | Additional notes about customer |
| `is_active` | Boolean | Default=True | Whether customer account is active |

**Relationships:**
- One-to-Many: `appointments` → List of Appointment objects
- One-to-Many: `preferences` → List of CustomerPreference objects

---

## Service Model
**File:** `models/service.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique service identifier |
| `name` | String(100) | Not Null, Unique | Service name (e.g., "Hot Spring Bath", "Bamboo Massage") |
| `service_type` | String(50) | Not Null | Type: "thermal_bath", "massage", "tea_therapy" |
| `description` | Text | Nullable | Detailed service description |
| `duration_minutes` | Integer | Not Null | Service duration in minutes |
| `price` | Float | Not Null, Check(>0) | Service price |
| `is_available` | Boolean | Default=True | Whether service is currently available |
| `max_capacity` | Integer | Default=1 | Maximum customers per service slot |
| `created_at` | DateTime | Default=now | Service creation timestamp |
| `popularity_score` | Float | Default=0.0 | Calculated popularity based on bookings |

**Relationships:**
- One-to-Many: `appointments` → List of Appointment objects

**Service Types:**
- `thermal_bath`: Thermal water baths
- `massage`: Various massage services
- `tea_therapy`: Tea therapy sessions

---

## Appointment Model
**File:** `models/appointment.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique appointment identifier |
| `customer_id` | Integer | Foreign Key → Customer.id, Not Null | Reference to customer |
| `service_id` | Integer | Foreign Key → Service.id, Not Null | Reference to service |
| `appointment_datetime` | DateTime | Not Null | Scheduled date and time |
| `status` | String(20) | Not Null, Default="scheduled" | Status: "scheduled", "completed", "cancelled", "no_show" |
| `duration_minutes` | Integer | Not Null | Actual duration (may differ from service default) |
| `price_paid` | Float | Not Null | Amount paid for this appointment |
| `notes` | Text | Nullable | Appointment-specific notes |
| `created_at` | DateTime | Default=now | Appointment creation timestamp |
| `completed_at` | DateTime | Nullable | When appointment was completed |
| `cancelled_at` | DateTime | Nullable | When appointment was cancelled |
| `cancellation_reason` | String(200) | Nullable | Reason for cancellation |

**Relationships:**
- Many-to-One: `customer` → Customer object
- Many-to-One: `service` → Service object
- One-to-One: `financial_record` → FinancialRecord object (if revenue recorded)

**Status Values:**
- `scheduled`: Appointment is booked
- `completed`: Service was provided
- `cancelled`: Appointment was cancelled
- `no_show`: Customer didn't show up

---

## FinancialRecord Model
**File:** `models/financial_record.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique financial record identifier |
| `transaction_type` | String(20) | Not Null | Type: "revenue" or "expense" |
| `amount` | Float | Not Null, Check(>0) | Transaction amount (always positive) |
| `description` | String(500) | Not Null | Description of transaction |
| `category` | String(50) | Not Null | Category: "service_revenue", "hot_water", "tea", "supplies", "other" |
| `supplier_id` | Integer | Foreign Key → Supplier.id, Nullable | Reference to supplier (for expenses) |
| `appointment_id` | Integer | Foreign Key → Appointment.id, Nullable | Reference to appointment (for revenue) |
| `transaction_date` | DateTime | Not Null, Default=now | When transaction occurred |
| `created_at` | DateTime | Default=now | Record creation timestamp |
| `receipt_number` | String(50) | Nullable, Unique | Receipt or invoice number |
| `notes` | Text | Nullable | Additional transaction notes |

**Relationships:**
- Many-to-One: `supplier` → Supplier object (optional, for expenses)
- Many-to-One: `appointment` → Appointment object (optional, for revenue)

**Transaction Types:**
- `revenue`: Income from services
- `expense`: Costs (hot water, tea, supplies, etc.)

**Categories:**
- Revenue: `service_revenue`
- Expenses: `hot_water`, `tea`, `supplies`, `equipment`, `maintenance`, `other`

---

## Supplier Model
**File:** `models/supplier.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique supplier identifier |
| `name` | String(100) | Not Null | Supplier name (e.g., "Bamboo Tea Co.", "Hot Springs Supply") |
| `supplier_type` | String(50) | Not Null | Type: "hot_water", "tea", "spa_supplies", "equipment", "other" |
| `contact_info` | String(200) | Nullable | Contact information |
| `address` | String(300) | Nullable | Supplier address/location |
| `is_active` | Boolean | Default=True | Whether supplier is currently used |
| `created_at` | DateTime | Default=now | Supplier record creation timestamp |
| `notes` | Text | Nullable | Additional supplier notes |

**Relationships:**
- One-to-Many: `financial_records` → List of FinancialRecord objects (expenses)

**Supplier Types:**
- `hot_water`: Thermal water suppliers
- `tea`: Tea suppliers
- `spa_supplies`: General spa supplies
- `equipment`: Spa equipment suppliers
- `other`: Miscellaneous suppliers

---

## CustomerPreference Model
**File:** `models/customer_preference.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique preference identifier |
| `customer_id` | Integer | Foreign Key → Customer.id, Not Null | Reference to customer |
| `service_id` | Integer | Foreign Key → Service.id, Not Null | Reference to service |
| `preference_score` | Float | Not Null, Default=0.0, Range(0.0-10.0) | Calculated preference score (0-10) |
| `visit_count` | Integer | Default=0 | Number of times customer booked this service |
| `last_visited` | DateTime | Nullable | Date of last booking for this service |
| `first_visited` | DateTime | Nullable | Date of first booking for this service |
| `average_rating` | Float | Nullable, Range(1.0-5.0) | Average rating if customer rates services |
| `total_spent` | Float | Default=0.0 | Total amount spent on this service |
| `preference_factors` | JSON | Nullable | Additional preference data (time preferences, etc.) |
| `created_at` | DateTime | Default=now | Preference record creation |
| `updated_at` | DateTime | Default=now, OnUpdate=now | Last update timestamp |

**Relationships:**
- Many-to-One: `customer` → Customer object
- Many-to-One: `service` → Service object

**Preference Score Calculation Factors:**
- Visit frequency
- Recency of visits
- Total spending
- Average rating (if available)
- Time preferences
- Service combination patterns

---

## ServiceRecommendation Model (Optional - for caching)
**File:** `models/service_recommendation.py`

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique recommendation identifier |
| `customer_id` | Integer | Foreign Key → Customer.id, Not Null | Reference to customer |
| `recommended_service_id` | Integer | Foreign Key → Service.id, Not Null | Recommended service |
| `recommendation_score` | Float | Not Null | Confidence score for recommendation |
| `recommendation_reason` | String(200) | Nullable | Why this service is recommended |
| `recommendation_type` | String(50) | Not Null | Type: "preference_based", "popular", "complementary", "seasonal" |
| `created_at` | DateTime | Default=now | Recommendation generation timestamp |
| `is_viewed` | Boolean | Default=False | Whether customer viewed this recommendation |
| `is_booked` | Boolean | Default=False | Whether customer booked based on recommendation |

**Relationships:**
- Many-to-One: `customer` → Customer object
- Many-to-One: `recommended_service` → Service object

---

## Database Schema Summary

### Table Relationships:
```
Customer (1) ──< (Many) Appointment
Service (1) ──< (Many) Appointment
Customer (1) ──< (Many) CustomerPreference
Service (1) ──< (Many) CustomerPreference
Supplier (1) ──< (Many) FinancialRecord
Appointment (1) ──< (0 or 1) FinancialRecord (revenue)
Customer (1) ──< (Many) ServiceRecommendation
Service (1) ──< (Many) ServiceRecommendation
```

### Indexes (for performance):
- `Customer.name` - for quick customer lookup
- `Appointment.appointment_datetime` - for scheduling queries
- `Appointment.status` - for filtering by status
- `FinancialRecord.transaction_date` - for financial reports
- `FinancialRecord.category` - for expense categorization
- `CustomerPreference.customer_id, service_id` - composite unique index
- `Service.service_type` - for filtering services by type


