-- This calculates the the SUM_winV(w, c_j)
select label, sum(count) as words 
from category_word_count
group by label;

-- Calculate the propability of word in category
set category = 0;

select cwc.*, t.words, (cwc.count/t.words) as prop
from category_word_count as cwc
inner join (select label, sum(count) as words 
     from category_word_count
     group by label) as t on t.label = cwc.label;