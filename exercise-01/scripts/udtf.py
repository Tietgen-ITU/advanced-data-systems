import re
import numpy as np
import csv
from collections import defaultdict

file_path = '/tmp/model/bayes.csv'

def write_data(label_probabilities, word_label_probabilities, distinct_words):
    with open(file_path, "w") as file:
        file.write(len(label_probabilities) + ";" + 2*len(distinct_words))

        for label, probability in label_probabilities.items():
            file.write(label + ";" + probability)

        for label in label_probabilities:
            for word in distinct_words:
                file.write(label + ";" + word + ";" + word_label_probabilities[(label, word)])

def read_data():
    with open(file_path, "r") as file:
        file.read()
    return 

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
        distinct_label_words = defaultdict(lambda: set())

        for label, text in training_data:
            for word in clean_text(text).split():
                distinct_words.add(word)
                distinct_label_words[label].add(word)
        
        return (distinct_words, {label:len(words) for label, words in distinct_label_words.items()})


    def __calc_word_probability(self, word_count, total_words_in_label, total_words):
        probability = (word_count+1)/(total_words_in_label+total_words)
        return self.min_value if self.min_value > probability else probability


    def build_classifier(self, training_data):
        labels_probability = self.__calculate_label_document_probabilities(training_data)
        label_words = [(label, clean_text(text).split()) for label, text in training_data] 
        words, label_distinct_word_count = self.__prepare_word_stats(training_data)
        V = len(words)
        label_word_count = self.__count_words_for_each_label(label_words)

        # For each word calculate the probability for all labels
        words_in_label_probabilities = defaultdict(lambda: self.min_value)
        for label in labels_probability:
            total_distinct_word_count_label = label_distinct_word_count[label]
            for word in words:
                words_in_label_probabilities[(label, word)] = self.__calc_word_probability(label_word_count[(label, word)], total_distinct_word_count_label, V)
        
        return self.BayesClassifier(words_in_label_probabilities, labels_probability)


    class BayesClassifier:

        def __init__(self, label_word_probabilities, label_probabilities):
            self.label_word_probabilities = label_word_probabilities
            self.label_probabilities = label_probabilities

        def __calculate_ranking(self, label, label_probability, words):
            probabilities = [self.label_word_probabilities[(label, word)] for word in words]
            word_probs = np.array(probabilities)

            ranking = np.log(label_probability) + np.sum(np.log(word_probs))
            return ranking


        def calculate(self, text):

            words = clean_text(text).split()

            rankings = []
            for label, label_probability in self.label_probabilities.items():
                ranking = self.__calculate_ranking(label, label_probability, words)
                rankings.append((label, ranking))

            return max(rankings, key=lambda x: x[1])

class CobraSentimentHandler:
    def __init__(self):
        self.training_data = []
        self.test_data = []

    def process(self, label, text, is_training_data):
        # Get training data and test data seperated
        if is_training_data:
            self.training_data.append((label, text))
        else:
            self.test_data.append((label, text))

    def end_partition(self):
        builder = BayesBuilder()
        classifier = builder.build_classifier(self.training_data)
        
        for target, text in self.test_data:
            predicted, rank = classifier.calculate(text)
            yield (target, predicted, rank, text)
        


if __name__ == '__main__':
    test_data_path = "./test-data/data.csv"

    data = []
    with open(test_data_path, "r") as file:
        csvreader = csv.reader(file, delimiter=';')

        for (label, text, is_training_data) in csvreader:
            data.append((int(label), text, is_training_data == "true"))
    

    udtf_handler = CobraSentimentHandler()
    for label, text, is_training_data in data:
        udtf_handler.process(label, text, is_training_data)

    results = udtf_handler.end_partition()

    for result in results:
        print(result)
