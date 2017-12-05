from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))

import json
import argparse
import pickle

from data_processing.utils import *
from collections import defaultdict, OrderedDict


def count_vocab(review, acc):
    text = review['text']
    for sentence in text:
        for word in sentence:
            if word.isnumeric():
                acc[NUMERICAL_TOKEN] += 1
            else:
                acc[word] += 1
    return acc


def main():
    parser = argparse.ArgumentParser(
        description="Constructs a vocabulary and associated frequency count from the tokenized reviews.")
    parser.add_argument(
        'review_path',
        help="The location of json file of reviews to count words in",
        type=str)
    parser.add_argument(
        'vocab_pickle',
        help="The location to save the pickled vocabulary to",
        type=str)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=restricted_int,
        default=5)
    parser.add_argument(
        '--threshold',
        metavar='n',
        help="The minimum number of times a word can occur without getting mapped to the <UNKNOWN> token",
        type=restricted_int,
        default=10)
    args = parser.parse_args()

    directory = os.path.dirname(args.vocab_pickle)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.review_path, 'r') as review_file, open(args.vocab_pickle, 'xb+') as vocab_pickle:
        print("Beginning vocab count!")
        num_reviews = sum(1 for _ in review_file)
        print("There are %d reviews." % num_reviews)
        review_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in review_file)

        vocab_dict = defaultdict(int)
        vocab_dict = apply_over_generator(
            reviews, count_vocab, acc=vocab_dict, num_elements=num_reviews, progress_interval=args.progress_interval)

        word_count = 0
        removed_count = 0
        freq_dict = {}
        for word, freq in vocab_dict.items():
            if freq < args.threshold:
                removed_count += 1
            else:
                word_count += 1
                freq_dict[word] = freq
        freq_dict[UNKNOWN_TOKEN] = removed_count
        # Highest to lowest frequency
        sorted_dict = OrderedDict(sorted(freq_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))
        pickle.dump(sorted_dict, vocab_pickle)
        print("There are %d words (not including %s), after removing %d." % (word_count, UNKNOWN_TOKEN, removed_count))
        print("Counting complete!")


if __name__ == '__main__':
    main()
