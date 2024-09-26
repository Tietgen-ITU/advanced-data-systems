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