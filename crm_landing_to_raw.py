
import boto3
import csv
import io
from datetime import datetime, timezone

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BUCKET = "ihcl-enterprise-data-lake"
LANDING_PREFIX = "landing/crm/"
RAW_PREFIX = "raw/crm/"

s3 = boto3.client("s3")

# Expected source files and their required columns
EXPECTED_FILES = {
    "customers/crm_customers_18112026.csv": [
        "CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "EMAIL",
        "PHONE", "DATE_OF_BIRTH", "GENDER", "CITY", "STATE",
        "COUNTRY", "REGISTRATION_DATE", "CUSTOMER_SEGMENT",
        "LOYALTY_TIER", "PREFERRED_CHANNEL", "MARKETING_CONSENT",
        "CUSTOMER_STATUS", "CREATED_AT", "UPDATED_AT"
    ],

    "interactions/crm_interactions_18112026.csv": [
        "INTERACTION_ID", "CUSTOMER_ID", "INTERACTION_DATE",
        "INTERACTION_TYPE", "CHANNEL", "SUBJECT", "DESCRIPTION",
        "HOTEL", "CITY", "PRIORITY", "INTERACTION_STATUS",
        "RESOLUTION_TIME_HOURS", "CUSTOMER_SATISFACTION_SCORE",
        "CREATED_AT"
    ],

    "campaigns/crm_campaign_master_18112026.csv": [
        "CAMPAIGN_ID", "CAMPAIGN_NAME", "CAMPAIGN_TYPE",
        "CHANNEL", "TARGET_AUDIENCE", "CAMPAIGN_START_DATE",
        "CAMPAIGN_END_DATE", "CAMPAIGN_BUDGET", "CAMPAIGN_STATUS"
    ],

    "campaigns/crm_campaign_activity_18112026.csv": [
        "CAMPAIGN_ACTIVITY_ID", "CAMPAIGN_ID", "CUSTOMER_ID",
        "CHANNEL", "SENT_DATE", "DELIVERY_STATUS", "OPEN_DATE",
        "CLICK_DATE", "CONVERSION_DATE", "RESPONSE_STATUS",
        "CONVERSION_VALUE", "CAMPAIGN_COST", "CREATED_AT"
    ]
}


def validate_csv(bucket, key, expected_columns):
    """Validate CSV structure and basic data quality."""

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read()

    if not content:
        raise ValueError("File is empty")

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    actual_columns = reader.fieldnames

    if actual_columns is None:
        raise ValueError("CSV header is missing")

    if actual_columns != expected_columns:
        raise ValueError(
            f"Column mismatch. Expected {expected_columns}, "
            f"received {actual_columns}"
        )

    row_count = 0

    for row in reader:
        if None in row:
            raise ValueError(
                f"Extra values detected at CSV row {row_count + 2}"
            )

        if any(value is None for value in row.values()):
            raise ValueError(
                f"Missing CSV fields at row {row_count + 2}"
            )

        row_count += 1

    if row_count == 0:
        raise ValueError("CSV contains no data rows")

    return len(content), row_count


# --------------------------------------------------
# LANDING TO RAW PROCESS
# --------------------------------------------------

print("\n========== CRM LANDING TO RAW ==========")

results = []

for relative_path, expected_columns in EXPECTED_FILES.items():

    landing_key = LANDING_PREFIX + relative_path
    raw_key = RAW_PREFIX + relative_path

    print(f"\nProcessing: {relative_path}")

    try:
        file_size, row_count = validate_csv(
            BUCKET,
            landing_key,
            expected_columns
        )

        # Copy only after validation succeeds.
        s3.copy_object(
            Bucket=BUCKET,
            CopySource={
                "Bucket": BUCKET,
                "Key": landing_key
            },
            Key=raw_key,
            MetadataDirective="COPY"
        )

        print("Validation: PASSED")
        print("Rows:", row_count)
        print("File size:", file_size)
        print("Copied to:", raw_key)

        results.append({
            "file": relative_path,
            "rows": row_count,
            "status": "SUCCESS"
        })

    except Exception as error:
        print("Validation/Copy: FAILED")
        print("Reason:", str(error))

        results.append({
            "file": relative_path,
            "rows": 0,
            "status": "FAILED"
        })


# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

print("\n========== FINAL INGESTION REPORT ==========")

for result in results:
    print(result)

successful = sum(
    result["status"] == "SUCCESS" for result in results
)

failed = len(results) - successful

print("\nSuccessful files:", successful)
print("Failed files:", failed)

if failed:
    raise SystemExit(
        "CRM Landing to Raw completed with failures."
    )

print("\nALL CRM FILES VALIDATED AND COPIED TO RAW")
print("Completed at:", datetime.now(timezone.utc).isoformat())