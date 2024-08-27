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

In order to upload the data I have followed the [guide from snowflake]()

