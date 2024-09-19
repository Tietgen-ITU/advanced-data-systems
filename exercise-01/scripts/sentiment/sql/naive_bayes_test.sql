set test_table = 'yelp_test';

-- Create a query to find best probability
create or replace temporary table reduced_test_documents as
select row_number() over (order by t.text) id, t.*
from table($test_table) as t
inner join labels as l on t.label = l.label;

create or replace temporary table test_words as
select et.id doc_id, sp.value, et.text
from reduced_test_documents as et, LATERAL split_to_table(clean_string(et.text), ' ') as sp
inner join (select distinct t.value from words t) w on w.value = sp.value;

-- Try to calculate propability of each label https://stackoverflow.com/questions/56489932/aggregate-function-to-multiply-all-values
create or replace table ranking as
select t.doc_id, pw.label, IFF(MIN(pw.word_prop) = 0, '-inf', ln(pw.label_prop) + (sum(ln(nullif(pw.word_prop,0))))) as rank, row_number() over (partition by t.doc_id order by rank desc) as id
from test_words as t
inner join propabilities as pw ON pw.value = t.value
GROUP BY t.doc_id, pw.label, pw.label_prop;

-- Get prediction results
create or replace temporary view prediction_results as
select r.doc_id, IFF(r.label = rtd.label, 'Correct', 'Not Correct') as status, r.label predicted, rtd.label target, rtd.text 
from ranking r
inner join reduced_test_documents as rtd on rtd.id = r.doc_id
where r.id = 1;

-- Uncomment below to see the rate of success of the predictions
-- with 
--     negative_results    as (select count(*) as negatives from prediction_results where predicted <> target),
--     positive_results    as (select count(*) as positives from prediction_results where predicted = target)
-- select positives / (positives + negatives) as success
-- from positive_results, negative_results