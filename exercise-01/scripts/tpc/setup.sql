-- Setup the specific warehouse
create or replace warehouse COBRA_WH
    with WAREHOUSE_SIZE = XSMALL;

create or replace warehouse COBRA_WH
    with WAREHOUSE_SIZE = SMALL;

create or replace warehouse COBRA_WH
    with WAREHOUSE_SIZE = MEDIUM;

create or replace warehouse COBRA_WH
    with WAREHOUSE_SIZE = LARGE;

-- Make sure that we point the script to the correct warehouse and database
use warehouse COBRA_WH;
use database SNOWFLAKE_SAMPLE_DATA;

-- Use the specific schema for the correct Scaling Factor(SF)
use schema TPCH_SF1;
use schema TPCH_SF10;
use schema TPCH_SF100;
use schema TPCH_SF1000;