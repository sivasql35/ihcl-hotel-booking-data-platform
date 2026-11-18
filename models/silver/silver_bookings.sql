
{{ config(
    materialized = 'table',
) }}

WITH source_data AS (

    SELECT *
    FROM IHCL_DB.BRONZE.BOOKINGS

),

cleaned_data AS (

    SELECT

        -- Technical booking identifier
        SHA2(
            CONCAT(
                COALESCE(SOURCE_FILE_NAME, ''),
                '|',
                COALESCE(TO_VARCHAR(FILE_ROW_NUMBER), '')
            ),
            256
        ) AS BOOKING_KEY,

        -- Hotel information
        NULLIF(TRIM(HOTEL), '') AS HOTEL,
        NULLIF(TRIM(CITY), '') AS CITY,
        NULLIF(UPPER(TRIM(COUNTRY)), '') AS COUNTRY,

        -- Booking status and lead time
        TRY_TO_NUMBER(NULLIF(TRIM(IS_CANCELED), ''))
            ::NUMBER(1,0) AS IS_CANCELED,

        TRY_TO_NUMBER(NULLIF(TRIM(LEAD_TIME), ''))
            ::NUMBER(10,0) AS LEAD_TIME,

        -- Arrival information
        TRY_TO_NUMBER(NULLIF(TRIM(ARRIVAL_DATE_YEAR), ''))
            ::NUMBER(4,0) AS ARRIVAL_DATE_YEAR,

        INITCAP(TRIM(ARRIVAL_DATE_MONTH))
            AS ARRIVAL_DATE_MONTH,

        TRY_TO_NUMBER(NULLIF(TRIM(ARRIVAL_DATE_WEEK_NUMBER), ''))
            ::NUMBER(2,0) AS ARRIVAL_DATE_WEEK_NUMBER,

        TRY_TO_NUMBER(NULLIF(TRIM(ARRIVAL_DATE_DAY_OF_MONTH), ''))
            ::NUMBER(2,0) AS ARRIVAL_DATE_DAY_OF_MONTH,

        CASE UPPER(TRIM(ARRIVAL_DATE_MONTH))
            WHEN 'JANUARY' THEN '01'
            WHEN 'FEBRUARY' THEN '02'
            WHEN 'MARCH' THEN '03'
            WHEN 'APRIL' THEN '04'
            WHEN 'MAY' THEN '05'
            WHEN 'JUNE' THEN '06'
            WHEN 'JULY' THEN '07'
            WHEN 'AUGUST' THEN '08'
            WHEN 'SEPTEMBER' THEN '09'
            WHEN 'OCTOBER' THEN '10'
            WHEN 'NOVEMBER' THEN '11'
            WHEN 'DECEMBER' THEN '12'
        END AS ARRIVAL_MONTH_NUMBER,

        -- Stay duration
        TRY_TO_NUMBER(NULLIF(TRIM(STAYS_IN_WEEKEND_NIGHTS), ''))
            ::NUMBER(5,0) AS STAYS_IN_WEEKEND_NIGHTS,

        TRY_TO_NUMBER(NULLIF(TRIM(STAYS_IN_WEEK_NIGHTS), ''))
            ::NUMBER(5,0) AS STAYS_IN_WEEK_NIGHTS,

        -- Guest information
        TRY_TO_NUMBER(NULLIF(TRIM(ADULTS), ''))
            ::NUMBER(5,0) AS ADULTS,

        TRY_TO_DECIMAL(NULLIF(TRIM(CHILDREN), ''), 5, 1)
            AS CHILDREN,

        TRY_TO_NUMBER(NULLIF(TRIM(BABIES), ''))
            ::NUMBER(5,0) AS BABIES,

        -- Booking channels and categories
        UPPER(NULLIF(TRIM(MEAL), '')) AS MEAL,
        INITCAP(NULLIF(TRIM(MARKET_SEGMENT), '')) AS MARKET_SEGMENT,
        INITCAP(NULLIF(TRIM(DISTRIBUTION_CHANNEL), ''))
            AS DISTRIBUTION_CHANNEL,

        TRY_TO_NUMBER(NULLIF(TRIM(IS_REPEATED_GUEST), ''))
            ::NUMBER(1,0) AS IS_REPEATED_GUEST,

        TRY_TO_NUMBER(NULLIF(TRIM(PREVIOUS_CANCELLATIONS), ''))
            ::NUMBER(10,0) AS PREVIOUS_CANCELLATIONS,

        TRY_TO_NUMBER(NULLIF(TRIM(PREVIOUS_BOOKINGS_NOT_CANCELED), ''))
            ::NUMBER(10,0) AS PREVIOUS_BOOKINGS_NOT_CANCELED,

        -- Room information
        UPPER(NULLIF(TRIM(RESERVED_ROOM_TYPE), ''))
            AS RESERVED_ROOM_TYPE,

        UPPER(NULLIF(TRIM(ASSIGNED_ROOM_TYPE), ''))
            AS ASSIGNED_ROOM_TYPE,

        TRY_TO_NUMBER(NULLIF(TRIM(BOOKING_CHANGES), ''))
            ::NUMBER(10,0) AS BOOKING_CHANGES,

        NULLIF(TRIM(DEPOSIT_TYPE), '') AS DEPOSIT_TYPE,

        -- Agent and company identifiers
        TRY_TO_NUMBER(NULLIF(TRIM(AGENT), ''))
            ::NUMBER(10,0) AS AGENT,

        TRY_TO_NUMBER(NULLIF(TRIM(COMPANY), ''))
            ::NUMBER(10,0) AS COMPANY,

        TRY_TO_NUMBER(NULLIF(TRIM(DAYS_IN_WAITING_LIST), ''))
            ::NUMBER(10,0) AS DAYS_IN_WAITING_LIST,

        INITCAP(NULLIF(TRIM(CUSTOMER_TYPE), ''))
            AS CUSTOMER_TYPE,

        -- Revenue and customer requests
        TRY_TO_DECIMAL(NULLIF(TRIM(ADR), ''), 12, 2)
            AS ADR,

        TRY_TO_NUMBER(NULLIF(TRIM(REQUIRED_CAR_PARKING_SPACES), ''))
            ::NUMBER(5,0) AS REQUIRED_CAR_PARKING_SPACES,

        TRY_TO_NUMBER(NULLIF(TRIM(TOTAL_OF_SPECIAL_REQUESTS), ''))
            ::NUMBER(5,0) AS TOTAL_OF_SPECIAL_REQUESTS,

        -- Reservation status
        UPPER(NULLIF(TRIM(RESERVATION_STATUS), ''))
            AS RESERVATION_STATUS,

        TRY_TO_TIMESTAMP_NTZ(
            NULLIF(TRIM(RESERVATION_STATUS_DATE), '')
        )::DATE AS RESERVATION_STATUS_DATE,

        -- Ingestion metadata
        SOURCE_FILE_NAME,
        FILE_ROW_NUMBER,
        FILE_LAST_MODIFIED,
        INGESTION_TIMESTAMP

    FROM source_data

)

SELECT
    * EXCLUDE (ARRIVAL_MONTH_NUMBER),

    TRY_TO_DATE(
        TO_VARCHAR(ARRIVAL_DATE_YEAR) || '-' ||
        ARRIVAL_MONTH_NUMBER || '-' ||
        LPAD(TO_VARCHAR(ARRIVAL_DATE_DAY_OF_MONTH), 2, '0'),
        'YYYY-MM-DD'
    ) AS ARRIVAL_DATE,

    COALESCE(ADULTS, 0)
        + COALESCE(CHILDREN, 0)
        + COALESCE(BABIES, 0) AS TOTAL_GUESTS,

    COALESCE(STAYS_IN_WEEKEND_NIGHTS, 0)
        + COALESCE(STAYS_IN_WEEK_NIGHTS, 0) AS TOTAL_STAY_NIGHTS,

    ADR < 0 AS IS_NEGATIVE_ADR,

    (
        COALESCE(STAYS_IN_WEEKEND_NIGHTS, 0)
        + COALESCE(STAYS_IN_WEEK_NIGHTS, 0)
    ) = 0 AS IS_ZERO_NIGHT_STAY,

    (
        COALESCE(ADULTS, 0)
        + COALESCE(CHILDREN, 0)
        + COALESCE(BABIES, 0)
    ) = 0 AS IS_ZERO_GUEST_BOOKING

FROM cleaned_data