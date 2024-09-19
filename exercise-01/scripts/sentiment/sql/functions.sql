-- A simple UDF that cleans the string and returns it in lower case. 
-- Credit: Adrian Borup (adbo)
create or replace function clean_string("str" string)
returns string
language javascript
STRICT IMMUTABLE
AS
$$
    return str.replace(/[^A-Za-z 0-9]/g, '').toLowerCase();
$$;

-- A view of the propability that a particular word appears in a document of a specific category
set min_number = 1e-322;

CREATE OR REPLACE FUNCTION calc_prop(word_count INTEGER, total_words_with_label INTEGER, total_words INTEGER) RETURNS FLOAT AS $$
    
    IFF($min_number > (word_count + 1) / (total_words_with_label + total_words), $min_number, (word_count + 1) / (total_words_with_label + total_words))
$$;