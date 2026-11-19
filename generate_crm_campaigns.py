
import random
from pathlib import Path
from datetime import datetime, date, timedelta

import pandas as pd

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

random.seed(200)

BASE_DIR = Path(r"C:\Users\Sivananda\ihcl_dbt\datasets\CRM")

CUSTOMER_FILE = BASE_DIR / "customers" / "crm_customers_18112026.csv"
CAMPAIGN_DIR = BASE_DIR / "campaigns"

CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)

CAMPAIGN_MASTER_FILE = CAMPAIGN_DIR / "crm_campaign_master_18112026.csv"
CAMPAIGN_ACTIVITY_FILE = CAMPAIGN_DIR / "crm_campaign_activity_18112026.csv"

TOTAL_ACTIVITIES = 5000

START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 11, 18)

# --------------------------------------------------
# LOAD CUSTOMER MASTER
# --------------------------------------------------

customers = pd.read_csv(
    CUSTOMER_FILE,
    parse_dates=["REGISTRATION_DATE"]
)

if customers["CUSTOMER_ID"].isna().any():
    raise ValueError("Customer master contains null CUSTOMER_ID values.")

if customers["CUSTOMER_ID"].duplicated().any():
    raise ValueError("Customer master contains duplicate CUSTOMER_ID values.")

customer_records = customers.to_dict("records")

# --------------------------------------------------
# CREATE CAMPAIGN MASTER
# --------------------------------------------------

campaign_definitions = [
    ("New Year Getaway", "SEASONAL", "EMAIL", "ALL"),
    ("Summer Escape", "SEASONAL", "MOBILE_APP", "ALL"),
    ("Monsoon Retreat", "SEASONAL", "EMAIL", "PREMIUM"),
    ("Festive Luxury Offers", "FESTIVE", "SMS", "ALL"),
    ("Diwali Special", "FESTIVE", "EMAIL", "GOLD"),
    ("Christmas Celebration", "FESTIVE", "MOBILE_APP", "ALL"),
    ("Weekend Stay Offers", "PROMOTIONAL", "SMS", "ALL"),
    ("Luxury Suite Upgrade", "UPSELL", "EMAIL", "PLATINUM"),
    ("Family Holiday Package", "PROMOTIONAL", "MOBILE_APP", "ALL"),
    ("Business Traveller Rewards", "RETENTION", "EMAIL", "BUSINESS"),
    ("Loyalty Tier Upgrade", "LOYALTY", "MOBILE_APP", "SILVER"),
    ("Exclusive Gold Benefits", "LOYALTY", "EMAIL", "GOLD"),
    ("Platinum Member Privileges", "LOYALTY", "SMS", "PLATINUM"),
    ("Birthday Celebration Offer", "PERSONALIZED", "EMAIL", "ALL"),
    ("Anniversary Special", "PERSONALIZED", "MOBILE_APP", "ALL"),
    ("Win Back Inactive Guests", "RETENTION", "SMS", "ALL"),
    ("Refer a Friend", "REFERRAL", "EMAIL", "ALL"),
    ("Luxury Dining Experience", "CROSS_SELL", "MOBILE_APP", "GOLD"),
    ("Spa and Wellness Package", "CROSS_SELL", "EMAIL", "ALL"),
    ("Early Bird Booking Offer", "PROMOTIONAL", "SMS", "ALL"),
    ("Long Stay Benefits", "PROMOTIONAL", "EMAIL", "ALL"),
    ("Premium Resort Experience", "UPSELL", "MOBILE_APP", "PLATINUM"),
    ("Tata Neu Member Benefits", "PARTNERSHIP", "EMAIL", "ALL"),
    ("Customer Appreciation", "RETENTION", "SMS", "ALL"),
    ("Always On Loyalty Rewards", "LOYALTY", "MOBILE_APP", "ALL")
]

campaign_rows = []

for index, definition in enumerate(campaign_definitions, start=1):

    campaign_name, campaign_type, channel, audience = definition

    campaign_start = START_DATE + timedelta(days=(index - 1) * 25)

    # Campaigns remain active through the project end date.
    campaign_end = END_DATE

    campaign_rows.append({
        "CAMPAIGN_ID": f"CAMP{index:04d}",
        "CAMPAIGN_NAME": campaign_name,
        "CAMPAIGN_TYPE": campaign_type,
        "CHANNEL": channel,
        "TARGET_AUDIENCE": audience,
        "CAMPAIGN_START_DATE": campaign_start,
        "CAMPAIGN_END_DATE": campaign_end,
        "CAMPAIGN_BUDGET": round(random.uniform(50000, 500000), 2),
        "CAMPAIGN_STATUS": "COMPLETED"
        if campaign_end < END_DATE else "ACTIVE"
    })

campaigns = pd.DataFrame(campaign_rows)

# --------------------------------------------------
# CREATE 5,000 CUSTOMER CAMPAIGN ACTIVITIES
# --------------------------------------------------

activity_rows = []

campaign_records = campaigns.to_dict("records")

for number in range(1, TOTAL_ACTIVITIES + 1):

    customer = random.choice(customer_records)

    customer_id = customer["CUSTOMER_ID"]
    registration_date = customer["REGISTRATION_DATE"].date()

    eligible_campaigns = [
        campaign for campaign in campaign_records
        if campaign["CAMPAIGN_START_DATE"] <= END_DATE
        and campaign["CAMPAIGN_END_DATE"] >= max(
            registration_date, START_DATE
        )
    ]

    if not eligible_campaigns:
        raise ValueError(
            f"No eligible campaign for customer {customer_id}"
        )

    campaign = random.choice(eligible_campaigns)

    earliest_date = max(
        registration_date,
        campaign["CAMPAIGN_START_DATE"],
        START_DATE
    )

    available_days = (END_DATE - earliest_date).days

    sent_date = earliest_date + timedelta(
        days=random.randint(0, available_days)
    )

    delivery_status = random.choices(
        ["DELIVERED", "BOUNCED"],
        weights=[96, 4],
        k=1
    )[0]

    open_date = None
    click_date = None
    conversion_date = None
    conversion_value = 0.0

    if delivery_status == "DELIVERED":

        opened = random.random() < 0.45

        if opened:
            open_date = sent_date + timedelta(
                days=random.randint(0, 3)
            )

            clicked = random.random() < 0.35

            if clicked:
                click_date = open_date + timedelta(
                    days=random.randint(0, 2)
                )

                converted = random.random() < 0.20

                if converted:
                    conversion_date = click_date + timedelta(
                        days=random.randint(0, 7)
                    )

                    conversion_value = round(
                        random.uniform(1500, 50000), 2
                    )

    if delivery_status == "BOUNCED":
        response_status = "BOUNCED"
    elif conversion_date is not None:
        response_status = "CONVERTED"
    elif click_date is not None:
        response_status = "CLICKED"
    elif open_date is not None:
        response_status = "OPENED"
    else:
        response_status = "NO_RESPONSE"

    activity_rows.append({
        "CAMPAIGN_ACTIVITY_ID": f"ACT{number:07d}",
        "CAMPAIGN_ID": campaign["CAMPAIGN_ID"],
        "CUSTOMER_ID": customer_id,
        "CHANNEL": campaign["CHANNEL"],
        "SENT_DATE": sent_date,
        "DELIVERY_STATUS": delivery_status,
        "OPEN_DATE": open_date,
        "CLICK_DATE": click_date,
        "CONVERSION_DATE": conversion_date,
        "RESPONSE_STATUS": response_status,
        "CONVERSION_VALUE": conversion_value,
        "CAMPAIGN_COST": round(random.uniform(2, 25), 2),
        "CREATED_AT": datetime.combine(
            sent_date,
            datetime.min.time()
        )
    })

activities = pd.DataFrame(activity_rows)

# --------------------------------------------------
# DATA QUALITY VALIDATIONS
# --------------------------------------------------

valid_customer_ids = set(customers["CUSTOMER_ID"])
valid_campaign_ids = set(campaigns["CAMPAIGN_ID"])

invalid_customer_refs = (
    ~activities["CUSTOMER_ID"].isin(valid_customer_ids)
).sum()

invalid_campaign_refs = (
    ~activities["CAMPAIGN_ID"].isin(valid_campaign_ids)
).sum()

duplicate_activity_ids = activities[
    "CAMPAIGN_ACTIVITY_ID"
].duplicated().sum()

null_customer_ids = activities["CUSTOMER_ID"].isna().sum()

null_campaign_ids = activities["CAMPAIGN_ID"].isna().sum()

invalid_delivery_events = (
    activities["DELIVERY_STATUS"].eq("BOUNCED")
    & (
        activities["OPEN_DATE"].notna()
        | activities["CLICK_DATE"].notna()
        | activities["CONVERSION_DATE"].notna()
    )
).sum()

invalid_click_events = (
    activities["CLICK_DATE"].notna()
    & activities["OPEN_DATE"].isna()
).sum()

invalid_conversion_events = (
    activities["CONVERSION_DATE"].notna()
    & activities["CLICK_DATE"].isna()
).sum()

invalid_event_dates = (
    (
        activities["OPEN_DATE"].notna()
        & (activities["OPEN_DATE"] < activities["SENT_DATE"])
    )
    |
    (
        activities["CLICK_DATE"].notna()
        & (
            activities["CLICK_DATE"]
            < activities["OPEN_DATE"].fillna(activities["SENT_DATE"])
        )
    )
    |
    (
        activities["CONVERSION_DATE"].notna()
        & (
            activities["CONVERSION_DATE"]
            < activities["CLICK_DATE"].fillna(activities["SENT_DATE"])
        )
    )
).sum()

customer_dates = activities.merge(
    customers[["CUSTOMER_ID", "REGISTRATION_DATE"]],
    on="CUSTOMER_ID",
    how="left"
)

activities_before_registration = (
    customer_dates["SENT_DATE"]
    <
    customer_dates["REGISTRATION_DATE"].dt.date
).sum()

print("\n========== CRM CAMPAIGN VALIDATION ==========")

print("Campaign master records:", len(campaigns))
print("Unique campaign IDs:", campaigns["CAMPAIGN_ID"].nunique())

print("\nCampaign activity records:", len(activities))
print(
    "Unique activity IDs:",
    activities["CAMPAIGN_ACTIVITY_ID"].nunique()
)

print("\nInvalid customer references:", invalid_customer_refs)
print("Invalid campaign references:", invalid_campaign_refs)
print("Duplicate activity IDs:", duplicate_activity_ids)
print("Null customer IDs:", null_customer_ids)
print("Null campaign IDs:", null_campaign_ids)
print("Invalid delivery events:", invalid_delivery_events)
print("Clicks without opens:", invalid_click_events)
print("Conversions without clicks:", invalid_conversion_events)
print("Invalid event date sequence:", invalid_event_dates)
print(
    "Activities before customer registration:",
    activities_before_registration
)

# --------------------------------------------------
# EXPORT ONLY AFTER ALL VALIDATIONS PASS
# --------------------------------------------------

checks = [
    invalid_customer_refs,
    invalid_campaign_refs,
    duplicate_activity_ids,
    null_customer_ids,
    null_campaign_ids,
    invalid_delivery_events,
    invalid_click_events,
    invalid_conversion_events,
    invalid_event_dates,
    activities_before_registration
]

if any(checks):
    raise ValueError(
        "Data quality validation failed. CSV files were not exported."
    )

campaigns.to_csv(CAMPAIGN_MASTER_FILE, index=False)
activities.to_csv(CAMPAIGN_ACTIVITY_FILE, index=False)

print("\nALL DATA QUALITY CHECKS PASSED")
print("\nFiles created:")
print(CAMPAIGN_MASTER_FILE)
print(CAMPAIGN_ACTIVITY_FILE)
