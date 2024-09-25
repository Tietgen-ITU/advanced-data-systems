set train_table = 'yelp_train';

-- Create a reduced set of documents based on the labels we want to see
create or replace temporary view reduced_documents as
select t.*
from table($train_table) as t
inner join labels as l on t.label = l.label;

create or replace table words as
select et.doc_id, et.label, value
from (reduced_documents) as et, 
    LATERAL split_to_table(clean_string(et.text), ' ') as sp
where value != '';

-- Selects for both present and non present words in every category
create or replace temporary view cross_label_words as
select l.label, w.value
from labels l
inner join words w on w.label = l.label or w.label != l.label
GROUP BY l.label, w.value;

-- Gets count of words for every category
create or replace table label_words as
select wc.label, wc.value, count(w.value) as word_count
from cross_label_words as wc
left outer join words as w on wc.label = w.label and wc.value = w.value
GROUP BY wc.label, wc.value;

-- Calculate the propability of a document being in a category
set total_num_documents = (select count(distinct doc_id)
                            from reduced_documents);

-- Calculates the propability that the document came from a particular label
create or replace temporary view label_propabilities as
select label, count(distinct doc_id) doc_count, (doc_count / $total_num_documents) as label_prop
from reduced_documents
group by label;

-- Calculate the propability of word in category
set V = (select count(distinct value) from label_words);

-- This calculates the the SUM_winV(w, c_j)
create or replace temporary view label_total_word_count as
select label, sum(word_count) as total_count_words_in_label 
from label_words
group by label;

create or replace table propabilities as
select lw.*, lwc.total_count_words_in_label, calc_prop(lw.word_count, lwc.total_count_words_in_label, $V) word_prop, lp.label_prop as label_prop, $V total_words
from label_words as lw
inner join label_total_word_count as lwc on lwc.label = lw.label
inner join label_propabilities as lp on lp.label = lwc.label;
