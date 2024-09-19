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