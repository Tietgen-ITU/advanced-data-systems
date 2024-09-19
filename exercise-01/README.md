# Report

This is the report describing the steps that I took in order to solve the exercise.

## Steps

### Setup Dev environment
First and foremost, in order to keep track of my work I created my own github repository. Since I need the training and test data from yelp, I wrote the following in my terminal:
```
git submodule add https://huggingface.co/datasets/Yelp/yelp_review_full 
```

Then in order to get the large files I wrote:
```
git lfs fetch
git lfs pull
```

### Load data into snowflake

In order to upload the data I have followed the [guide from snowflake](https://docs.snowflake.com/en/user-guide/tutorials/script-data-load-transform-parquet#prerequisites).
Below is the resulting script:


```sql
create database COBRA_DB;
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

PUT file://~/advanced-data-systems/exercise-01/yelp_review_full/yelp_review_full/train-00000-of-00001.parquet @stage_anti_ex1;

PUT file://~/advanced-data-systems/exercise-01/yelp_review_full/yelp_review_full/test-00000-of-00001.parquet @stage_anti_ex1;

copy into yelp_train
    from (select $1:label::int,
                $1:text::varchar,
                row_number() over (order by $1:text::varchar)
         from @stage_anti_ex1/train-00000-of-00001.parquet);

copy into yelp_test
    from (select $1:label::int,
                $1:text::varchar
         from @stage_anti_ex1/test-00000-of-00001.parquet);
```

### Create small test setup

Here is the script to create the small test setup defined in the slides about naive bayes sentiment analysis:

```sql
create or replace table exercise_train (
    label INT,
    text VARCHAR,
    doc_id INT
);

create or replace table exercise_test (
    label INT,
    text VARCHAR
);

insert into EXERCISE_TRAIN (label, text, doc_id) VALUES
    (0, 'just plain boring', 1),
    (0, 'entirely predictable and lacks energy', 2),
    (0, 'no surprises and very few laughs', 3),
    (4, 'very powerful', 4),
    (4, 'the most fun film of the summer', 5);

insert into EXERCISE_TEST (label, text) VALUES
    (0, 'predictable with no fun');
```
