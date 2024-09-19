use WAREHOUSE ANIMAL_TASK_WH;
use DATABASE COBRA_DB;

create or replace table yelp_train (
    label INT,
    text VARCHAR,
    doc_id INT
);

create or replace table yelp_test (
    label INT,
    text VARCHAR
);

create file FORMAT anti_parquet
  TYPE = parquet;

create temporary stage stage_anti_ex1
FILE_FORMAT = anti_parquet;

PUT file:///Users/andreastietgen/dev/uni/msc/semester-3/ads/advanced-data-systems/exercise-01/yelp_review_full/yelp_review_full/train-00000-of-00001.parquet @stage_anti_ex1;

PUT file:///Users/andreastietgen/dev/uni/msc/semester-3/ads/advanced-data-systems/exercise-01/yelp_review_full/yelp_review_full/test-00000-of-00001.parquet @stage_anti_ex1;

copy into yelp_train
    from (select $1:label::int,
                $1:text::varchar,
                row_number() over (order by $1:text::varchar)
         from @stage_anti_ex1/train-00000-of-00001.parquet);

copy into yelp_test
    from (select $1:label::int,
                $1:text::varchar
         from @stage_anti_ex1/test-00000-of-00001.parquet);