-- SCRIPT TO INSTALL AND CALL THE JAVA UDTF
set train_table = 'yelp_train';
set test_table = 'yelp_test';

create or replace table bayes_train as
    select label, text
    from table($train_table)
    where label = 0 or label = 4;

create or replace table bayes_test as
    select label, text
    from table($test_table)
    where label = 0 or label = 4;

create or replace file FORMAT anti_csv
  TYPE = 'CSV'
  FIELD_DELIMITER = ';'
  COMPRESSION = NONE;

create or replace stage stage_anti_csv
    FILE_FORMAT = anti_csv;
    
create or replace function train_classifier(label INTEGER, text TEXT)
returns table (label INTEGER, word TEXT, label_probability float, word_probability float)
language python
runtime_version=3.11
packages = ('numpy')
handler='CobraSentimentHandler'
as $$
import re
from collections import defaultdict

# Cleans the text such that it only contains letters and returns it in lower_case
def clean_text(text):
    return re.sub(r'[^A-Za-z 0-9]', '', text).lower()

# Handles calculations for Naive Bayes classifier for the sentiment analysis
class BayesBuilder:
    def __init__(self) -> None:
        self.min_value = 1e-322

    # This creates what is equivalent to my 'label_words' table
    def __count_words_for_each_label(self, label_words):
        label_word_count = defaultdict(lambda: 0)

        for label, words in label_words:
            for word in words:
                label_word_count[(label, word)] += 1
        
        return label_word_count
    
    def __calculate_label_document_probabilities(self, training_data):

        document_count = len(training_data)
        label_document_count = defaultdict(lambda: 0)
        label_probability = defaultdict(lambda: 0)

        # Get the amount of documents in each label
        for (label, document) in training_data:
            label_document_count[label] += 1

        # For each label calculate the probability
        for label, count in label_document_count.items():
            label_probability[label] = (count/document_count)

        return label_probability

    def __prepare_word_stats(self, training_data):
        distinct_words = set()
        total_label_words = defaultdict(lambda: 0)

        for label, text in training_data:
            for word in clean_text(text).split():
                distinct_words.add(word)
                total_label_words[label] += 1
        
        return (distinct_words, total_label_words)


    def __calc_word_probability(self, word_count, total_word_in_label, total_words):
        probability = (word_count+1)/(total_word_in_label+total_words)
        return self.min_value if self.min_value > probability else probability


    def build_classifier(self, training_data):
        labels_probability = self.__calculate_label_document_probabilities(training_data)
        label_words = [(label, clean_text(text).split()) for label, text in training_data] 
        words, total_label_word_count = self.__prepare_word_stats(training_data)
        V = len(words)
        label_word_count = self.__count_words_for_each_label(label_words)

        # For each word calculate the probability for all labels
        words_in_label_probabilities = defaultdict(lambda: self.min_value)
        for label in labels_probability:
            total_distinct_word_count_label = total_label_word_count[label]
            for word in words:
                words_in_label_probabilities[(label, word)] = self.__calc_word_probability(label_word_count[(label, word)], total_distinct_word_count_label, V)
        
        return self.BayesClassifier(words_in_label_probabilities, labels_probability)


    class BayesClassifier:

        def __init__(self, label_word_probabilities, label_probabilities):
            self.label_word_probabilities = label_word_probabilities
            self.label_probabilities = label_probabilities
        
        def output_metadata(self):
            for (label, word), word_probability in self.label_word_probabilities.items():
                label_probability = self.label_probabilities[label]
                yield (label, word, label_probability, word_probability)

class CobraSentimentHandler:
    def __init__(self):
        self.training_data = []

    def process(self, label, text):
        # Get training data and test data seperated
        self.training_data.append((label, text))

    def end_partition(self):
        builder = BayesBuilder()
        classifier = builder.build_classifier(self.training_data)
        
        for label, word, label_probability, word_probability in classifier.output_metadata():
            yield (label, word, label_probability, word_probability)
$$;


-- Train the model
COPY INTO @stage_anti_csv/model.csv
FROM(SELECT results.*
        FROM bayes_train as u,
            TABLE(train_classifier(u.label, u.text) over ()) AS results)
single=true
overwrite=true
max_file_size=4900000000;

create or replace function bayes_classify(label INTEGER, text TEXT)
returns table (expected_label INTEGER, predicted_label INTEGER, ranking NUMBER, text TEXT)
language python
runtime_version=3.11
packages = ('numpy')
imports=('@stage_anti_csv/model.csv')
handler='CobraSentimentHandler'
as $$
import re
import numpy as np
import csv
import os
import sys

# Cleans the text such that it only contains letters and returns it in lower_case
def clean_text(text):
    return re.sub(r'[^A-Za-z 0-9]', '', text).lower()

# Handles the reading and pre-processing of the model metadata
class BayesBuilder:

    # Reads the model data at the specified path
    def read_model_data(self, path):
        with open(path, "r") as f:
            csvreader = csv.reader(f, delimiter=';')

            for (label, word, label_probability, word_probability) in csvreader:
                yield int(label), word, float(label_probability), float(word_probability)

    def build_classifier_from_model(self, model_file_path):

        label_probabilities = {}
        words_in_label_probabilities = {}
        words = set()

        for label, word, label_probability, word_probability in self.read_model_data(model_file_path):
            words.add(word)
            label_probabilities[label] = label_probability
            words_in_label_probabilities[(label, word)] = word_probability

        return self.BayesClassifier(words_in_label_probabilities, label_probabilities, words)

    # The classifier that calculates the rankings of the text belonging to a specific label
    class BayesClassifier:

        def __init__(self, label_word_probabilities, label_probabilities, words):
            self.label_word_probabilities = label_word_probabilities
            self.label_probabilities = label_probabilities
            self.words = words

        def __calculate_ranking(self, label, label_probability, words):
            probabilities = [self.label_word_probabilities[(label, word)] for word in words]
            word_probs = np.array(probabilities)

            ranking = np.log(label_probability) + np.sum(np.log(word_probs))
            return ranking

        # Predicts the label that the text belongs to 
        def predict(self, text):

            text_words = clean_text(text).split()
            known_words = [word for word in text_words if word in self.words]

            rankings = []
            for label, label_probability in self.label_probabilities.items():
                ranking = self.__calculate_ranking(label, label_probability, known_words)
                rankings.append((label, ranking))

            return max(rankings, key=lambda x: x[1])

class CobraSentimentHandler:
    def __init__(self):
        self.data = []

    def process(self, label, text):
        self.data.append((label, text))

    def end_partition(self):
        model_file_path = os.path.join(sys._xoptions["snowflake_import_directory"], 'model.csv')

        builder = BayesBuilder()
        classifier = builder.build_classifier_from_model(model_file_path)
        
        for target, text in self.data:
            predicted, rank = classifier.predict(text)
            yield (target, predicted, rank, text)
$$;

-- Uncomment the following code to run the model
-- -- Predict on test data
-- CREATE OR REPLACE TABLE bayes_udtf_predictions AS
-- SELECT results.*
-- FROM (bayes_test) AS u,
--     TABLE(bayes_classify(u.label, u.text) over ()) AS results;

-- -- Show the success rate
-- with 
--     negative_results    as (select count(*) as negatives from bayes_udtf_predictions where predicted_label <> expected_label),
--     positive_results    as (select count(*) as positives from bayes_udtf_predictions where predicted_label = expected_label)
-- select positives / (positives + negatives) as success
-- from positive_results, negative_results;