udtf_train = """
COPY INTO @stage_anti_csv/model.csv
FROM bayes_train AS u,
    TABLE(train_classifier(u.label, u.text) over ()) AS results)
single=true
max_file_size=4900000000;
"""

udtf_query = """
SELECT results.*
FROM (bayes_test) AS u,
    TABLE(bayes_predict(u.label, u.text, u.is_training) over ()) AS results;
"""