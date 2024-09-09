-- This calculates the the SUM_winV(w, c_j)
select label, sum(count) as words 
from category_word_count
group by label;

-- Calculate the propability of a document being in a category
set total_num_documents = (select count(doc_id)
                            from exercise_train);
create or replace view prop_document_category as
select label, count(doc_id) doc_count, (doc_count / $total_num_documents) as prop_doc
from exercise_train
group by label;

select *
from prop_document_category;

-- Calculate the propability of word in category
set word_count = (select count(distinct value) from category_word_count);

-- A view of the propability that a particular word appears in a document of a specific category
create or replace view prop_words as
select cwc.*, t.words, (cwc.count+1/(t.words+$word_count)) as word_prop, pdc.prop_doc as label_prop
from category_word_count as cwc
inner join (select label, sum(count) as words 
     from category_word_count
     group by label) as t on t.label = cwc.label
inner join prop_document_category as pdc on pdc.label = t.label;

select * 
from prop_words;

-- Create a query to find best probability
select sp.seq, sp.value, et.text
from exercise_test as et, LATERAL split_to_table(et.text, ' ') as sp;

-- Try to calculate propability of each label https://stackoverflow.com/questions/56489932/aggregate-function-to-multiply-all-values
create or replace view ranking as
select t.seq, pw.label, ln(pw.label_prop) + (sum(ln(pw.word_prop))) as rank, row_number() over (order by rank) as id
from (select sp.seq, sp.value, et.text
        from exercise_test as et, LATERAL split_to_table(et.text, ' ') as sp) as t
inner join prop_words as pw ON pw.value = t.value
GROUP BY t.seq, pw.label, pw.label_prop
order by rank desc;

select * 
from ranking;

-- Get top ranked for each calculation
select * 
from ranking as r
inner join (select seq, max(rank) as max_rank 
            from ranking
group by seq) as tr on tr.seq = r.seq
where tr.max_rank = r.rank;
