
{{ config(materialized='table') }}

WITH BOOKINGS AS (

    SELECT *
    FROM {{ ref('silver_bookings') }}

),

FACT AS (

    SELECT
        -- Identifiers
        B.BOOKING_KEY,
        H.HOTEL_KEY,
        D.DATE_KEY,

        -- Booking details
        B.IS_CANCELED,
        B.RESERVATION_STATUS,
        B.RESERVATION_STATUS_DATE,

        -- Arrival and stay information
        B.ARRIVAL_DATE,
        B.LEAD_TIME,
        B.STAYS_IN_WEEKEND_NIGHTS,
        B.STAYS_IN_WEEK_NIGHTS,
        B.TOTAL_STAY_NIGHTS,

        -- Guest information
        B.ADULTS,
        B.CHILDREN,
        B.BABIES,
        B.TOTAL_GUESTS,
        B.IS_REPEATED_GUEST,

        -- Revenue and booking measures
        B.ADR,
        B.BOOKING_CHANGES,
        B.PREVIOUS_CANCELLATIONS,
        B.PREVIOUS_BOOKINGS_NOT_CANCELED,
        B.DAYS_IN_WAITING_LIST,
        B.REQUIRED_CAR_PARKING_SPACES,
        B.TOTAL_OF_SPECIAL_REQUESTS,

        -- Booking classifications
        B.MEAL,
        B.MARKET_SEGMENT,
        B.DISTRIBUTION_CHANNEL,
        B.RESERVED_ROOM_TYPE,
        B.ASSIGNED_ROOM_TYPE,
        B.DEPOSIT_TYPE,
        B.CUSTOMER_TYPE,

        -- Agent and company
        B.AGENT,
        B.COMPANY,

        -- Data quality indicators
        B.IS_NEGATIVE_ADR,
        B.IS_ZERO_NIGHT_STAY,
        B.IS_ZERO_GUEST_BOOKING,

        -- Source lineage
        B.SOURCE_FILE_NAME,
        B.FILE_ROW_NUMBER,
        B.FILE_LAST_MODIFIED,
        B.INGESTION_TIMESTAMP

    FROM BOOKINGS B

    LEFT JOIN {{ ref('dim_hotel') }} H
        ON UPPER(TRIM(B.HOTEL)) = UPPER(TRIM(H.HOTEL))
       AND UPPER(TRIM(B.CITY)) = UPPER(TRIM(H.CITY))

    LEFT JOIN {{ ref('dim_date') }} D
        ON B.ARRIVAL_DATE = D.FULL_DATE

)

SELECT *
FROM FACT
