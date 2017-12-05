from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))

import json
import os

from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from data_processing.utils import apply_over_generator
from functools import partial


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


def clean_review_text(review):
    """Cleans a review string by tokenizing it, lemmatizing it, and removing stopwords and non alpha-numeric chars."""
    tokens = generate_tokens(review)
    lemmatized = lemmatize_tokens(tokens)
    return remove_stopwords(lemmatized)


def clean_json(cleaned_file, the_json, acc):
    cleaned_text = clean_review_text(the_json['text'])
    the_json['text'] = cleaned_text
    json.dump(the_json, cleaned_file)
    cleaned_file.write('\n')
    return acc+1


def main():
    parser = argparse.ArgumentParser(
        description="Cleans the reviews by tokenizing, lemmatizing, " +
        "removing stopwords and non alpha-numeric characters.")
    parser.add_argument(
        'dirty_path',
        help="The location of the \"dirty\" json file to clean",
        type=str)
    parser.add_argument(
        'clean_path',
        help="The location to save the cleaned json file to",
        type=str)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=int,
        default=5)
    args = parser.parse_args()

    directory = os.path.dirname(args.clean_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.dirty_path, 'r') as dirty_file, open(args.clean_path, 'x+') as cleaned_file:
        print("Beginning cleaning!")
        num_reviews = sum(1 for _ in dirty_file)
        print("There are %d reviews." % num_reviews)
        dirty_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in dirty_file)
        fn = partial(clean_json, cleaned_file)
        filtered_count = 0
        filtered_count = apply_over_generator(
            reviews, fn, acc=filtered_count, num_elements=num_reviews, progress_interval=args.progress_interval)

        if filtered_count != num_reviews:
            print(("ERROR! The filtered review count was %d but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (filtered_count, num_reviews))
            return -1
        print("Lemmatization complete!")


if __name__ == "__main__":
    main()
