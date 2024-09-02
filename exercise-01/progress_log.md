# Report

This is the report descriping the steps that I took in order to solve the exercise.

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

Now I need to upload the data into snowflake. In order to do so, in the snowsql client, I created a database:

```sql
create database COBRA_DB;
```

Now I need to set the warehouse that I have to use and the database that I want to use:

```sql
use WAREHOUSE ANIMAL_TASK_WH;
use DATABASE COBRA_DB;
```

In order to upload the data I have followed the [guide from snowflake](https://docs.snowflake.com/en/user-guide/tutorials/script-data-load-transform-parquet#prerequisites). So we start by creating the table:

```sql
create or replace table yelp_train (
    label INT,
    text VARCHAR
);

create or replace table yelp_test (
    label INT,
    text VARCHAR
);
```

After that I created a stage so that I could add files that later is needed to import data in the two tables:

```sql
create file FORMAT anti_parquet
  TYPE = parquet;

create temporary stage stage_anti_ex1
FILE_FORMAT = anti_parquet;
```

I add the files:
```
PUT file:///Users/andreastietgen/dev/uni/msc/semester-3/ads/ad
                                     vanced-data-systems/exercise-01/yelp_review_full/yelp_review_f
                                     ull/train-00000-of-00001.parquet @stage_anti_ex1;

PUT file:///Users/andreastietgen/dev/uni/msc/semester-3/ads/ad
                                     vanced-data-systems/exercise-01/yelp_review_full/yelp_review_f
                                     ull/test-00000-of-00001.parquet @stage_anti_ex1;
```

And then I copy the data into the tables:
```sql
copy into yelp_train
    from (select $1:label::int,
                $1:text::varchar
         from @stage_anti_ex1/train-00000-of-00001.parquet);

copy into yelp_test
    from (select $1:label::int,
                $1:text::varchar
         from @stage_anti_ex1/test-00000-of-00001.parquet);
```

And now the data is inserted.

### Create small test setup
Here is the script to create the small test setup defined in the slides about naive bayes sentiment analysis:
```sql
create or replace table exercise_test (
    label INT,
    text VARCHAR
);
create or replace table exercise_train (
    label INT,
    text VARCHAR
);

insert into EXERCISE_TRAIN (label, text) VALUES
    (0, 'just plain boring'),
    (0, 'entirely predictable and lacks energy'),
    (0, 'no surprises and very few laughs'),
    (4, 'very powerful'),
    (4, 'the most fun film of the summer');

insert into EXERCISE_TEST (label, text) VALUES
    (0, 'predictable with no fun');
```

### Implementation of word counts in categories
For the word count in each category the essential thing was to first split each sentence by `' '` and insert each word as an entry with the corresponding category that it was a part of(see line 0-)

The hard part is that not every word is a part of every category. To fix that, I had to join each category with each word, no matter if it was present or not. This resulted in a "view" that I could use to right join with the original words view, such that the words for a specific category would display `null` if that particular word is not present in that particular category.