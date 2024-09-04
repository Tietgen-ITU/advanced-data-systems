-- This calculates the the SUM_winV(w, c_j)
select label, sum(count) as words 
from category_word_count
group by label;