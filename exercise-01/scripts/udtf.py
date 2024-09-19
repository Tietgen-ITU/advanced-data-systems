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
