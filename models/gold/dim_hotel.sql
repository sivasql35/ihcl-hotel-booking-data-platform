
{{ config(materialized='table') }}

SELECT
    SHA2(
        UPPER(TRIM(HOTEL)) || '|' || UPPER(TRIM(CITY)),
        256
    ) AS HOTEL_KEY,

    HOTEL,
    CITY,
    COUNTRY,

    CURRENT_TIMESTAMP()::TIMESTAMP_NTZ AS CREATED_AT

FROM {{ ref('silver_bookings') }}

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
        UPPER(TRIM(HOTEL)),
        UPPER(TRIM(CITY))
    ORDER BY HOTEL
) = 1
