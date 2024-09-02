-- Splits each word into its own entry with its corresponding label
create or replace view words as
select et.label, value
FROM EXERCISE_TRAIN as et, LATERAL split_to_table(et.text, ' ') as sp;

select * from words;

-- Gets the distinct labels
select et.label, 
from (select distinct el.label from exercise_train as el) et;

-- Selects for both present and non present words in every category
select et.label, w.value
from (select distinct el.label from exercise_train as el) et
inner join words as w on w.label = et.label or w.label != et.label
GROUP BY et.label, w.value;

-- Gets count of words for every category
create or replace view category_word_count as
select wc.label, wc.value, count(w.value) as count
from (select et.label, w.value
      from (select distinct el.label from exercise_train as el) et
      inner join words as w on w.label = et.label or w.label != et.label
      GROUP BY et.label, w.value) as wc
left outer join words as w on wc.label = w.label and wc.value = w.value
GROUP BY wc.label, wc.value;
