udtf_train = """
COPY INTO @stage_anti_csv/model.csv
FROM(SELECT results.*
        FROM bayes_train as u,
            TABLE(train_classifier(u.label, u.text) over ()) AS results)
single=true
overwrite=true
max_file_size=4900000000;
"""

udtf_query = """
SELECT results.*
FROM (bayes_test) AS u,
    TABLE(bayes_classify(u.label, u.text) over ()) AS results;
"""