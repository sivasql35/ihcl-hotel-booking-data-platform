
import random
from pathlib import Path
from datetime import date, datetime, timedelta

import pandas as pd
from faker import Faker

# --------------------------------------------------
# Configuration
# --------------------------------------------------

random.seed(42)
Faker.seed(42)
fake = Faker("en_IN")

TOTAL_CUSTOMERS = 10_000

OUTPUT_DIR = (
    Path(r"C:\Users\Sivananda\ihcl_dbt")
    / "datasets"
    / "CRM"
    / "customers"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Reference data
# --------------------------------------------------

locations = [
    ("Bengaluru", "Karnataka", "India"),
    ("Mumbai", "Maharashtra", "India"),
    ("Delhi", "Delhi", "India"),
    ("Hyderabad", "Telangana", "India"),
    ("Chennai", "Tamil Nadu", "India"),
    ("Pune", "Maharashtra", "India"),
    ("Kolkata", "West Bengal", "India"),
    ("Ahmedabad", "Gujarat", "India"),
    ("Jaipur", "Rajasthan", "India"),
    ("Kochi", "Kerala", "India"),
    ("Goa", "Goa", "India"),
    ("London", "England", "United Kingdom"),
    ("Dubai", "Dubai", "UAE"),
    ("Singapore", "Singapore", "Singapore"),
    ("New York", "New York", "United States"),
    ("Sydney", "New South Wales", "Australia"),
]

segments = ["LEISURE", "BUSINESS", "PREMIUM", "CORPORATE"]
segment_weights = [45, 25, 20, 10]

loyalty_tiers = ["MEMBER", "SILVER", "GOLD", "PLATINUM"]
loyalty_weights = [55, 25, 15, 5]

channels = ["EMAIL", "SMS", "MOBILE_APP", "WEBSITE"]
channel_weights = [40, 20, 25, 15]

statuses = ["ACTIVE", "INACTIVE", "DORMANT"]
status_weights = [78, 12, 10]

genders = ["MALE", "FEMALE", "OTHER", "NOT_DISCLOSED"]
gender_weights = [48, 43, 2, 7]

# --------------------------------------------------
# Generate customer master
# --------------------------------------------------

customers = []

start_date = date(2018, 1, 1)
end_date = date(2026, 11, 17)

date_range_days = (end_date - start_date).days

for i in range(1, TOTAL_CUSTOMERS + 1):

    customer_id = f"CUST{i:07d}"

    first_name = fake.first_name()
    last_name = fake.last_name()

    city, state, country = random.choice(locations)

    registration_date = start_date + timedelta(
        days=random.randint(0, date_range_days)
    )

    date_of_birth = fake.date_of_birth(
        minimum_age=18,
        maximum_age=85
    )

    customer_segment = random.choices(
        segments,
        weights=segment_weights,
        k=1
    )[0]

    loyalty_tier = random.choices(
        loyalty_tiers,
        weights=loyalty_weights,
        k=1
    )[0]

    preferred_channel = random.choices(
        channels,
        weights=channel_weights,
        k=1
    )[0]

    customer_status = random.choices(
        statuses,
        weights=status_weights,
        k=1
    )[0]

    gender = random.choices(
        genders,
        weights=gender_weights,
        k=1
    )[0]

    # Synthetic email using reserved example domains
    email = (
        f"{customer_id.lower()}@example.com"
    )

    # Synthetic phone numbers; not intended for contact
    phone = f"+999{random.randint(1000000000, 9999999999)}"

    marketing_consent = random.choices(
        [True, False],
        weights=[72, 28],
        k=1
    )[0]

    created_at = datetime.combine(
        registration_date,
        datetime.min.time()
    ) + timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    updated_at = created_at + timedelta(
        days=random.randint(0, 180)
    )

    customers.append({
        "CUSTOMER_ID": customer_id,
        "FIRST_NAME": first_name,
        "LAST_NAME": last_name,
        "EMAIL": email,
        "PHONE": phone,
        "DATE_OF_BIRTH": date_of_birth,
        "GENDER": gender,
        "CITY": city,
        "STATE": state,
        "COUNTRY": country,
        "REGISTRATION_DATE": registration_date,
        "CUSTOMER_SEGMENT": customer_segment,
        "LOYALTY_TIER": loyalty_tier,
        "PREFERRED_CHANNEL": preferred_channel,
        "MARKETING_CONSENT": marketing_consent,
        "CUSTOMER_STATUS": customer_status,
        "CREATED_AT": created_at,
        "UPDATED_AT": updated_at
    })

# --------------------------------------------------
# Export CSV
# --------------------------------------------------

df = pd.DataFrame(customers)

output_file = OUTPUT_DIR / "crm_customers_18112026.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

# --------------------------------------------------
# Basic validation
# --------------------------------------------------

print("\nCRM CUSTOMER DATA GENERATION COMPLETED")
print("--------------------------------------")
print(f"Output file       : {output_file}")
print(f"Total records     : {len(df)}")
print(f"Unique customers  : {df['CUSTOMER_ID'].nunique()}")
print(f"Duplicate IDs     : {df['CUSTOMER_ID'].duplicated().sum()}")
print(f"Null customer IDs : {df['CUSTOMER_ID'].isna().sum()}")

print("\nCustomer segment distribution:")
print(df["CUSTOMER_SEGMENT"].value_counts())

print("\nLoyalty tier distribution:")
print(df["LOYALTY_TIER"].value_counts())

print("\nCountry distribution:")
print(df["COUNTRY"].value_counts())

print("\nSample records:")
print(df.head(5).to_string(index=False))
