# Database Schema Documentation

This document outlines the database schema, focusing on client management, service allocation, and user-outlet relationships. The schema is implemented using SQLAlchemy ORM with PostgreSQL-compatible data types.

---

## Table Overview

### 1. Clients (`clients`)
**Purpose**: Stores client organizations using the system  
**Columns**:
- `id` (Integer, PK): Unique client identifier
- `username` (String(50)): Display name
- `email` (String(255), Unique): Login credential
- `hashed_password` (String(255)): Secured authentication
- `is_active` (Boolean): Account status (default: True)
- `accesstype` (String(50)): Permission level
- `created_at`/`updated_at` (DateTime): Timestamps in IST

**Relationships**:
- One-to-Many with: Outlets, Users, Brands
- Cascading delete for child entities

**Example Data**:
```python
{
  "id": 1,
  "username": "FoodWorks",
  "email": "tech@foodworks.in",
  "is_active": True,
  "accesstype": "admin",
  "created_at": "2024-02-15 09:30:00+05:30"
}
```

---

### 2. Brands (`brands`)
**Purpose**: Manages brand entities under clients  
**Columns**:
- `brandname` (String(255), Unique): Brand identifier
- `client_id` (Integer, FK to clients.id): Parent organization

**Relationships**:
- Many-to-One with Client
- One-to-Many with Outlets

**Example**:
```python
{
  "id": 10,
  "brandname": "QuickBites",
  "client_id": 1,
  "created_at": "2024-02-15 10:00:00+05:30"
}
```

---

### 3. Outlets (`outlets`)
**Purpose**: Tracks physical/store locations  
**Key Columns**:
- `aggregator` (String(50)): Platform name (e.g., "Swiggy", "Zomato")
- `resid` (String(20)): Platform-specific ID
- Unique constraint: (`aggregator`, `resid`)
- `brand_id`: Associated brand

**Relationships**:
- Many-to-One with Brand and Client
- Many-to-Many with Services through `outlet_services`
- Many-to-Many with Users through `user_outlets`

**Example**:
```python
{
  "id": 100,
  "aggregator": "Swiggy",
  "resid": "SWG123",
  "brand_id": 10,
  "is_active": True,
  "outletnumber": "OUT-IND-001"
}
```

---

### 4. Users (`users`)
**Purpose**: Manages individual user accounts  
**Notable Columns**:
- `usernumber` (String(20), Unique): Internal identifier
- `useremail` (String(255), Unique): Contact/Login
- Unique constraint: (`usernumber`, `useremail`)

**Relationships**:
- Many-to-One with Client
- Many-to-Many with Services and Outlets

**Example**:
```python
{
  "id": 500,
  "usernumber": "EMP-204",
  "useremail": "manager@foodworks.in",
  "client_id": 1
}
```

---

### 5. Services (`services`)
**Purpose**: Catalog of available services  
**Columns**:
- `servicename` (String(50)): e.g., "Delivery", "Inventory"
- `servicevariant` (String(50)): e.g., "Premium", "Standard"

**Example**:
```python
{
  "id": 20,
  "servicename": "Analytics",
  "servicevariant": "Advanced"
}
```

---

## Junction Tables

### 6. OutletService (`outlet_services`)
**Purpose**: Links outlets to enabled services  
**Structure**:
- `outlet_id` + `service_id` (Unique pair)
- `client_id`: Owning organization

**Example**:
```python
{"outlet_id": 100, "service_id": 20, "client_id": 1}
```

---

### 7. UserService (`user_services`)
**Purpose**: Associates users with permitted services  
**Structure**:
- `user_id` + `service_id` (Unique pair)
- `client_id`: Parent organization

---

### 8. UserOutlet (`user_outlets`)
**Purpose**: Manages user access to specific outlets  
**Structure**:
- `user_id` + `outlet_id` (Unique pair)
- `client_id`: Owning client

---

## Key Features

1. **Data Integrity**:
   - Cascade delete rules (`delete-orphan`) maintain consistency
   - Composite unique constraints prevent duplicate relationships

2. **Temporal Tracking**:
   - Automatic timestamps (IST timezone)
   - `created_at` on insertion
   - `updated_at` on modification

3. **Relationship Model**:
   ```mermaid
   erDiagram
     CLIENTS ||--o{ USERS : "1-m"
     CLIENTS ||--o{ BRANDS : "1-m"
     BRANDS ||--o{ OUTLETS : "1-m"
     OUTLETS }o--o{ SERVICES : "m-m via outlet_services"
     USERS }o--o{ SERVICES : "m-m via user_services"
     USERS }o--o{ OUTLETS : "m-m via user_outlets"
   ```

4. **Enums**:
   - `StatusEnum` provides standardized status options (Active/Inactive/All)

---

## Usage Notes

- **Time Zones**: All timestamps use IST (UTC+5:30)
- **Identifiers**:
  - External IDs (e.g., `resid`, `usernumber`) use String type for flexibility
  - Internal IDs (PKs) are auto-incrementing integers
- **Security**:
  - Passwords are stored hashed (never plaintext)
  - Email addresses are unique and indexed for fast lookups

This schema supports complex client hierarchies while maintaining performance through proper indexing and relationship constraints. Developers should leverage the ORM relationships for querying rather than manual joins to ensure data consistency.