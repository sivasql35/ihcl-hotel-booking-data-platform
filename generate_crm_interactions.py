
import random
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

random.seed(100)
Faker.seed(100)
fake = Faker("en_IN")

BASE_DIR = Path(r"C:\Users\Sivananda\ihcl_dbt")

CUSTOMER_FILE = (
    BASE_DIR
    / "datasets"
    / "CRM"
    / "customers"
    / "crm_customers_18112026.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "CRM"
    / "interactions"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "crm_interactions_18112026.csv"

TOTAL_INTERACTIONS = 25_000

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 11, 18, 23, 59, 59)

# --------------------------------------------------
# 2. LOAD CUSTOMER MASTER
# --------------------------------------------------

if not CUSTOMER_FILE.exists():
    raise FileNotFoundError(
        f"Customer master not found: {CUSTOMER_FILE}"
    )

customers = pd.read_csv(
    CUSTOMER_FILE,
    parse_dates=["REGISTRATION_DATE"]
)

customer_records = customers.to_dict("records")

if not customer_records:
    raise ValueError("Customer master contains no records")

print("Customer master loaded:", len(customer_records))

# --------------------------------------------------
# 3. REFERENCE DATA
# --------------------------------------------------

interaction_types = [
    "BOOKING_ENQUIRY",
    "GENERAL_ENQUIRY",
    "COMPLAINT",
    "FEEDBACK",
    "ROOM_UPGRADE_REQUEST",
    "CANCELLATION_REQUEST",
    "LOYALTY_ENQUIRY",
    "SPECIAL_REQUEST"
]

interaction_type_weights = [20, 18, 15, 15, 8, 8, 10, 6]

channels = [
    "EMAIL",
    "PHONE",
    "WEBSITE",
    "MOBILE_APP"
]

channel_weights = [30, 25, 20, 25]

priorities = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]

priority_weights = [25, 45, 25, 5]

statuses = [
    "OPEN",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED"
]

status_weights = [5, 10, 35, 50]

hotels = [
    ("City Hotel - Bengaluru", "Bengaluru"),
    ("Resort Hotel - Goa", "Goa"),
    ("City Hotel - Mumbai", "Mumbai"),
    ("City Hotel - Delhi", "Delhi"),
    ("Resort Hotel - Jaipur", "Jaipur"),
    ("City Hotel - Hyderabad", "Hyderabad"),
    ("Resort Hotel - Kochi", "Kochi"),
    ("City Hotel - Chennai", "Chennai"),
    ("City Hotel - Kolkata", "Kolkata"),
    ("Resort Hotel - Udaipur", "Udaipur")
]

subjects = {
    "BOOKING_ENQUIRY": [
        "Room availability enquiry",
        "Reservation confirmation",
        "Rate plan enquiry"
    ],
    "GENERAL_ENQUIRY": [
        "Hotel facilities enquiry",
        "Check-in and check-out information",
        "Airport transfer enquiry"
    ],
    "COMPLAINT": [
        "Room cleanliness concern",
        "Service delay complaint",
        "Billing discrepancy"
    ],
    "FEEDBACK": [
        "Stay experience feedback",
        "Staff service appreciation",
        "Food and dining feedback"
    ],
    "ROOM_UPGRADE_REQUEST": [
        "Room category upgrade",
        "Suite availability request"
    ],
    "CANCELLATION_REQUEST": [
        "Reservation cancellation",
        "Refund status enquiry"
    ],
    "LOYALTY_ENQUIRY": [
        "Loyalty points balance",
        "Membership tier enquiry",
        "Points redemption enquiry"
    ],
    "SPECIAL_REQUEST": [
        "Early check-in request",
        "Late checkout request",
        "Dietary preference request"
    ]
}

descriptions = {
    "BOOKING_ENQUIRY":
        "Customer contacted the hotel regarding reservation options and availability.",

    "GENERAL_ENQUIRY":
        "Customer requested general information about hotel services and facilities.",

    "COMPLAINT":
        "Customer reported an issue and requested assistance from the service team.",

    "FEEDBACK":
        "Customer shared feedback about the hotel experience.",

    "ROOM_UPGRADE_REQUEST":
        "Customer requested information about available room upgrades.",

    "CANCELLATION_REQUEST":
        "Customer contacted support regarding cancellation and refund options.",

    "LOYALTY_ENQUIRY":
        "Customer requested assistance with loyalty membership or reward points.",

    "SPECIAL_REQUEST":
        "Customer submitted a special request related to their hotel stay."
}

# --------------------------------------------------
# 4. GENERATE INTERACTIONS
# --------------------------------------------------

interactions = []

for i in range(1, TOTAL_INTERACTIONS + 1):

    # Select customer and registration date together
    customer = random.choice(customer_records)

    customer_id = customer["CUSTOMER_ID"]

    registration_date = customer["REGISTRATION_DATE"].to_pydatetime()

    # Business rule:
    # Interaction must happen on or after registration
    effective_start = max(
        START_DATE,
        registration_date
    )

    if effective_start > END_DATE:
        raise ValueError(
            f"Customer {customer_id} has an invalid registration date"
        )

    available_seconds = int(
        (END_DATE - effective_start).total_seconds()
    )

    interaction_date = effective_start + timedelta(
        seconds=random.randint(0, available_seconds)
    )

    # Generate interaction attributes
    interaction_type = random.choices(
        interaction_types,
        weights=interaction_type_weights,
        k=1
    )[0]

    channel = random.choices(
        channels,
        weights=channel_weights,
        k=1
    )[0]

    priority = random.choices(
        priorities,
        weights=priority_weights,
        k=1
    )[0]

    status = random.choices(
        statuses,
        weights=status_weights,
        k=1
    )[0]

    hotel, city = random.choice(hotels)

    resolution_time = (
        round(random.uniform(0.5, 72), 2)
        if status in ["RESOLVED", "CLOSED"]
        else None
    )

    satisfaction_score = (
        random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 8, 17, 35, 35],
            k=1
        )[0]
        if status in ["RESOLVED", "CLOSED"]
        else None
    )

    interactions.append({

        "INTERACTION_ID": f"INT{i:08d}",

        "CUSTOMER_ID": customer_id,

        "INTERACTION_DATE": interaction_date,

        "INTERACTION_TYPE": interaction_type,

        "CHANNEL": channel,

        "SUBJECT": random.choice(
            subjects[interaction_type]
        ),

        "DESCRIPTION": descriptions[interaction_type],

        "HOTEL": hotel,

        "CITY": city,

        "PRIORITY": priority,

        "INTERACTION_STATUS": status,

        "RESOLUTION_TIME_HOURS": resolution_time,

        "CUSTOMER_SATISFACTION_SCORE": satisfaction_score,

        "CREATED_AT": interaction_date

    })

# --------------------------------------------------
# 5. CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(interactions)

# --------------------------------------------------
# 6. DATA QUALITY VALIDATIONS
# --------------------------------------------------

valid_customer_ids = set(
    customers["CUSTOMER_ID"]
)

invalid_customer_references = (
    ~df["CUSTOMER_ID"].isin(valid_customer_ids)
).sum()

duplicate_interaction_ids = (
    df["INTERACTION_ID"].duplicated().sum()
)

null_customer_ids = (
    df["CUSTOMER_ID"].isna().sum()
)

null_interaction_dates = (
    df["INTERACTION_DATE"].isna().sum()
)

# Check interaction date against registration date
validation_df = df.merge(
    customers[["CUSTOMER_ID", "REGISTRATION_DATE"]],
    on="CUSTOMER_ID",
    how="left"
)

interactions_before_registration = (
    validation_df["INTERACTION_DATE"].dt.date
    < validation_df["REGISTRATION_DATE"].dt.date
).sum()

# --------------------------------------------------
# 7. EXPORT CSV
# --------------------------------------------------

if (
    invalid_customer_references > 0
    or duplicate_interaction_ids > 0
    or null_customer_ids > 0
    or null_interaction_dates > 0
    or interactions_before_registration > 0
):
    raise ValueError(
        "CRM interaction data quality validation failed. "
        "CSV was not exported."
    )

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

# --------------------------------------------------
# 8. FINAL REPORT
# --------------------------------------------------

print("\nCRM INTERACTIONS GENERATED")
print("--------------------------------------")

print("Total records:", len(df))

print(
    "Unique interaction IDs:",
    df["INTERACTION_ID"].nunique()
)

print(
    "Duplicate interaction IDs:",
    duplicate_interaction_ids
)

print(
    "Null customer IDs:",
    null_customer_ids
)

print(
    "Invalid customer references:",
    invalid_customer_references
)

print(
    "Null interaction dates:",
    null_interaction_dates
)

print(
    "Interactions before registration:",
    interactions_before_registration
)

print("\nInteraction type distribution:")
print(df["INTERACTION_TYPE"].value_counts())

print("\nChannel distribution:")
print(df["CHANNEL"].value_counts())

print("\nInteraction status distribution:")
print(df["INTERACTION_STATUS"].value_counts())

print("\nSample records:")
print(df.head(5).to_string(index=False))

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nALL DATA QUALITY CHECKS PASSED")
