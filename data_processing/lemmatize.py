from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import json
import os
import sys

from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from time import time


def get_wordnet_pos(treebank_tag):
    """Map treebank tags to wordnet tags.

    From https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    """

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Default to noun when unknown POS is found.


def generate_tokens(review, do_pos=True):
    """Yields a nested list indexed by [sentence, word] populated either by words, or (word, pos) tuples."""
    sent_tokens = sent_tokenize(review)
    result = []
    for sentence in sent_tokens:
        word_tokens = word_tokenize(sentence)
        word_tokens = [word.lower() for word in word_tokens]
        if do_pos:
            word_tokens = pos_tag(word_tokens, tagset='universal')
            word_tokens = [(word, get_wordnet_pos(tag)) for word, tag in word_tokens]
        result.append(word_tokens)

    return result


def lemmatize_word(word, pos):
    """Lemmatize a single word."""
    return lemmatize_word.lemmatizer(word, pos)
lemmatize_word.lemmatizer=WordNetLemmatizer().lemmatize


def lemmatize_tokens(review):
    """Lemmatize a review's tokens. Review should be POS tagged.

    Args:
        review: A nested list of depth 2 with indexing [sentence, word_loc]. Each element is a tuple of (word, pos_tag).

    Returns:
        A nested list of depth 2 with indexing [sentence, word_loc]. Each element is a lemmatized word.
    """
    return [[lemmatize_word(*i) for i in sentence] for sentence in review]


def remove_stopwords(review):
    """Remove stopwords and non-alphanumeric characters from the review."""
    return [[word for word in sentence if (word.isalnum() and word not in remove_stopwords.s_words)]
            for sentence in review]
remove_stopwords.s_words = set(stopwords.words('english'))


def clean_review(review):
    """Cleans a review by tokenizing it, lemmatizing it, and removing stopwords and non alpha-numeric characters."""
    tokens = generate_tokens(review)
    lemmatized = lemmatize_tokens(tokens)
    return remove_stopwords(lemmatized)


def main():
    num_args = len(sys.argv)
    if num_args <= 1:
        raise ValueError("Need to specify the path to save the file at!")
    save_path = sys.argv[1]
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    if num_args is 3:
        progress_interval = int(sys.argv[2])
    else:
        progress_interval = 10  # Progress printing interval in seconds.

    with open('data/review.json', 'r') as dirty_file, open('processed/review.json', 'w+') as cleaned_file:
        print("Beginning Cleaning!")
        num_reviews = sum(1 for line in dirty_file)
        print("There are %d reviews." % num_reviews)
        dirty_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in dirty_file)
        last_time = time()
        last_i = 0
        for i, review in enumerate(reviews):
            cleaned_text = clean_review(review['text'])
            review['text'] = cleaned_text
            json.dump(review, cleaned_file)
            current_time = time()
            delta = current_time - last_time
            if delta >= progress_interval:
                average_speed = (i - last_i) / delta
                est_time_remaining = (num_reviews-i) / average_speed
                last_i = i
                last_time = current_time
                print("Percent Complete: %7.4f, Est. Minutes Remaining: %6.1f" % (i/num_reviews * 100, est_time_remaining/60))


if __name__ == "__main__":
    main()
