\# Hotel Booking Data Engineering Platform

\### AWS S3 | Snowflake | Snowpipe | dbt Core | SQL



\## 1. Project Overview



This project demonstrates an end-to-end cloud data engineering pipeline for processing hotel booking data using AWS S3, Snowflake, Snowpipe, and dbt Core.



The platform ingests booking CSV files from Amazon S3 into Snowflake using automated Snowpipe ingestion. dbt Core then transforms the raw booking records into standardized Silver datasets and analytics-ready Gold dimensional models.



The final Gold layer supports hotel-level booking analysis, cancellation-rate monitoring, average daily rate (ADR) analysis, and room-night reporting.



\*\*Note:\*\* This is a portfolio project using a public/synthetic hotel booking dataset. It is not an implementation using IHCL's proprietary production data.



\## 2. Architecture



```text

&#x20;            Hotel Booking CSV Files

&#x20;                      |

&#x20;                      v

&#x20;                AWS S3 Bucket

&#x20;                      |

&#x20;                      v

&#x20;             S3 Event Notification

&#x20;                      |

&#x20;                      v

&#x20;                Amazon SQS

&#x20;                      |

&#x20;                      v

&#x20;             Snowflake Snowpipe

&#x20;                      |

&#x20;                      v

&#x20;             SNOWFLAKE BRONZE

&#x20;                 BOOKINGS

&#x20;                      |

&#x20;                      v

&#x20;                 dbt CORE

&#x20;                      |

&#x20;                      v

&#x20;             SNOWFLAKE SILVER

&#x20;              SILVER\_BOOKINGS

&#x20;                      |

&#x20;                      v

&#x20;                 dbt CORE

&#x20;                      |

&#x20;           +----------+----------+

&#x20;           |                     |

&#x20;           v                     v

&#x20;       DIM\_HOTEL              DIM\_DATE

&#x20;           |                     |

&#x20;           +----------+----------+

&#x20;                      |

&#x20;                      v

&#x20;                FACT\_BOOKINGS

&#x20;                      |

&#x20;                      v

&#x20;            MART\_HOTEL\_PERFORMANCE

&#x20;                      |

&#x20;                      v

&#x20;             Business Analytics

```



\## 3. Technology Stack



| Technology | Purpose |

|---|---|

| AWS S3 | Cloud storage and source-file landing zone |

| AWS IAM | Secure access between AWS and Snowflake |

| Amazon SQS | Event notification delivery for Snowpipe |

| Snowflake | Cloud data warehouse |

| Snowpipe | Automated file ingestion |

| dbt Core | SQL-based data transformation and testing |

| SQL | Data cleansing, modelling and analytics |

| Git | Version control |



\## 4. Data Pipeline Implementation



\### Step 1: AWS S3 – Data Landing



\- Created an S3 bucket named `ihcl-enterprise-data-lake`.

\- Configured a dedicated source prefix:



&#x20; `raw/pms/bookings/`



\- Uploaded hotel booking CSV files into the landing zone.

\- Used separate source filenames to distinguish ingestion batches.

\- Preserved the original source files for traceability and reprocessing.



\### Step 2: Snowflake – Secure S3 Integration



Configured Snowflake access to AWS S3 using:



\- Storage integration: `IHCL\_INBOUND\_INT`

\- External stage: `IHCL\_DB.BRONZE.IHCL\_PMS\_BOOKINGS\_STAGE`

\- File format: `IHCL\_DB.BRONZE.IHCL\_PMS\_CSV\_FORMAT`



Configured IAM permissions and trust relationships for secure access between Snowflake and AWS.



\### Step 3: Snowpipe – Automated Ingestion



Implemented Snowpipe with S3 event notifications and Amazon SQS.



Snowpipe automatically loads new CSV files from the S3 landing prefix into the Snowflake Bronze table.



Implemented:

\- Header-based column matching.

\- Case-insensitive column mapping.

\- Source filename tracking.

\- Source row-number tracking.

\- File modification timestamp tracking.

\- Ingestion timestamp tracking.



\### Step 4: Snowflake Bronze Layer



Created the Bronze table:



`IHCL\_DB.BRONZE.BOOKINGS`



The Bronze layer preserves source values as text and adds ingestion metadata.



Metadata columns:



\- `SOURCE\_FILE\_NAME`

\- `FILE\_ROW\_NUMBER`

\- `FILE\_LAST\_MODIFIED`

\- `INGESTION\_TIMESTAMP`



This provides source-level traceability and helps investigate ingestion issues.



\### Step 5: dbt Silver Layer



Created the dbt model:



`IHCL\_DB.SILVER.SILVER\_BOOKINGS`



Transformations include:



\- Data type conversion.

\- Trimming and standardization.

\- Numeric and date transformations.

\- Derived arrival date.

\- Total guest calculation.

\- Total stay-night calculation.

\- Technical booking key generation.

\- Data quality anomaly flags.



Generated a deterministic SHA-256 technical key using source filename and source row number.



```sql

SHA2(

&#x20;   CONCAT(

&#x20;       COALESCE(SOURCE\_FILE\_NAME, ''),

&#x20;       '|',

&#x20;       COALESCE(TO\_VARCHAR(FILE\_ROW\_NUMBER), '')

&#x20;   ),

&#x20;   256

) AS BOOKING\_KEY

```



This key identifies a source record. It is not a real PMS reservation identifier.



\### Step 6: dbt Gold Layer – Dimensional Modelling



Implemented a dimensional model consisting of two dimensions, one fact table, and one business mart.



\*\*DIM\_HOTEL\*\*



\- One row per distinct hotel and city combination.

\- Generates a deterministic hotel key.

\- Stores hotel, city, and country attributes.



\*\*DIM\_DATE\*\*



\- Generates a continuous calendar date dimension.

\- Includes year, quarter, month, week, day, and weekend attributes.

\- Uses `YYYYMMDD` as the date key.



\*\*FACT\_BOOKINGS\*\*



\- Stores booking-level measures and attributes.

\- Connects bookings to hotel and date dimensions.

\- Includes booking status, ADR, guests, stay nights, and source metadata.



\*\*MART\_HOTEL\_PERFORMANCE\*\*



\- Aggregates booking metrics at hotel level.

\- Calculates cancellation rate.

\- Calculates average ADR.

\- Calculates average guests per booking.

\- Summarizes total room nights.



\## 5. Data Quality and Validation



Implemented dbt schema tests to validate the transformed datasets.



Examples:



\- `not\_null`

\- `unique`

\- `accepted\_values`

\- `relationships`



Validation results from the completed build:



| Model | Records |

|---|---:|

| SILVER\_BOOKINGS | 119,500 |

| DIM\_HOTEL | 31 |

| DIM\_DATE | 1,458 |

| FACT\_BOOKINGS | 119,500 |

| MART\_HOTEL\_PERFORMANCE | 31 |



\*\*Full dbt build result:\*\*



\- Models built: 5

\- Data tests passed: 31

\- Total successful operations: 36

\- Warnings: 0

\- Errors: 0



Command:



```bash

dbt build

```



\### Data Anomaly Investigation



Investigated potential data quality anomalies, including:



\- Negative ADR values.

\- Zero-night stays.

\- Zero-guest bookings.

\- Potential duplicate booking records.



The identified anomaly records were retained for investigation rather than automatically deleted.



Potential business duplicates were not removed because the dataset does not contain a reliable PMS reservation ID. The generated technical key identifies source rows, not actual reservations.



\## 6. Business Analytics



The Gold mart supports the following metrics:



| Metric | Description |

|---|---|

| Total Bookings | Number of booking records |

| Canceled Bookings | Number of canceled records |

| Not Canceled Bookings | Number of non-canceled records |

| Cancellation Rate | Canceled records as a percentage of total records |

| Average ADR | Average daily rate across booking records |

| Average Guests | Average guests per booking |

| Total Room Nights | Sum of recorded stay nights |



\### Observed Results



Based on the completed dataset:



\- Total booking records: 119,500

\- Total canceled records: 44,231

\- Total non-canceled records: 75,269

\- Overall cancellation rate: 37.01%

\- Hotel dimension records: 31



These figures describe the portfolio dataset and should not be interpreted as actual IHCL operational performance.



\## 7. dbt Lineage



The dbt documentation lineage graph demonstrates the transformation dependencies:



```text

silver\_bookings

&#x20;     |

&#x20;     +------ dim\_hotel

&#x20;     |

&#x20;     +------ dim\_date

&#x20;     |

&#x20;     +------ fact\_bookings

&#x20;                   |

&#x20;                   v

&#x20;         mart\_hotel\_performance

```



Generated documentation using:



```bash

dbt docs generate

dbt docs serve --port 8081

```



The lineage graph helps understand model dependencies and the flow of data from Silver to Gold.



\## 8. Project Structure



```text

ihcl\_dbt/

│

├── analyses/

│

├── macros/

│   └── generate\_schema\_name.sql

│

├── models/

│   ├── example/

│   │

│   ├── silver/

│   │   ├── silver\_bookings.sql

│   │   └── schema.yml

│   │

│   └── gold/

│       ├── dim\_hotel.sql

│       ├── dim\_date.sql

│       ├── fact\_bookings.sql

│       ├── mart\_hotel\_performance.sql

│       └── schema.yml

│

├── seeds/

├── snapshots/

├── tests/

├── dbt\_project.yml

└── README.md

```



Credentials and private keys are maintained locally and must not be committed to Git.



\## 9. Running the dbt Project



Install the required dbt packages in your Python environment:



```bash

pip install dbt-core dbt-snowflake

```



Configure the Snowflake connection in `profiles.yml` using your own account credentials and authentication settings.



Validate the connection:



```bash

dbt debug

```



Parse the project:



```bash

dbt parse

```



Run all models and tests:



```bash

dbt build

```



Generate documentation:



```bash

dbt docs generate

```



Serve documentation locally:



```bash

dbt docs serve --port 8081

```



\## 10. Key Engineering Concepts Demonstrated



\- Cloud object storage using AWS S3.

\- Secure AWS-to-Snowflake integration.

\- Event-driven ingestion using Snowpipe.

\- Bronze, Silver, and Gold architecture.

\- SQL-based ELT transformations using dbt Core.

\- SHA-256 deterministic technical keys.

\- Dimensional modelling and fact/dimension relationships.

\- Data quality testing and anomaly investigation.

\- Source-level data lineage and auditability.

\- Business-oriented aggregation and reporting.



\## 11. Future Enhancements



Potential next improvements:



\- Incremental dbt models for efficient processing of new batches.

\- Automated orchestration and scheduled dbt execution.

\- CI/CD integration using GitHub Actions.

\- Monitoring and alerting for ingestion failures.

\- Reconciliation between S3 source files and Snowflake Bronze.

\- Additional analytical marts and dashboard integration.



\## 12. Conclusion



This project demonstrates an end-to-end data engineering workflow using AWS, Snowflake, and dbt Core.



It covers automated data ingestion, secure cloud integration, SQL-based transformations, dimensional modelling, data quality validation, lineage documentation, and business analytics.



The implementation provides a practical demonstration of modern cloud data engineering concepts and SQL-based ELT development.

