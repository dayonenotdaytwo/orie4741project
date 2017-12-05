from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))

import json
import argparse
import pickle
import numpy as np

from data_processing.utils import *
from functools import partial


def main():
    parser = argparse.ArgumentParser(
        description="Maps the tokenized reviews onto the provided vocabulary.")
    parser.add_argument(
        'review_path',
        help="The location of json file of tokenized reviews to map over",
        type=str)
    parser.add_argument(
        'vocab_pickle',
        help="The location of the vocabulary pickle file",
        type=str)
    parser.add_argument(
        'mapped_vocab_path',
        help="The location of the json file to save the vocab mapped json to",
        type=str)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=restricted_int,
        default=5)
    parser.add_argument(
        '--map_to_index',
        help='Whether the text gets mapped to its index in the vocabulary or not',
        default=False,
        type=bool)
    args = parser.parse_args()

    directory = os.path.dirname(args.mapped_vocab_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.review_path, 'r') as review_file,\
            open(args.vocab_pickle, 'rb') as vocab_pickle,\
            open(args.mapped_vocab_path, 'x+') as mapped_vocab_file:
        print("Beginning vocabulary mapping!")
        num_reviews = sum(1 for _ in review_file)
        print("There are %d reviews." % num_reviews)

        vocab_dict = pickle.load(vocab_pickle)
        num_words = len(vocab_dict)
        vocab_list = list(key for key, _ in vocab_dict.items())
        print("There are %d words in the vocabulary." % num_words)

        review_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in review_file)

        unknown_idx = vocab_list.index(UNKNOWN_TOKEN)
        numerical_idx = vocab_list.index(NUMERICAL_TOKEN)

        def map_word_to_vocab(word):
            if word.isnumeric():
                if args.map_to_index:
                    return numerical_idx
                else:
                    return NUMERICAL_TOKEN
            try:
                if args.map_to_index:
                    return vocab_list.index(word)
                else:
                    return word
            except ValueError:
                if args.map_to_index:
                    return unknown_idx
                else:
                    return UNKNOWN_TOKEN

        def map_to_vocab(review, acc):
            text = review['text']
            review['text'] = [[map_word_to_vocab(word) for word in sentence] for sentence in text]
            json.dump(review, mapped_vocab_file)
            mapped_vocab_file.write('\n')
            return acc + 1

        apply_count = 0
        apply_count = apply_over_generator(
            reviews, map_to_vocab, acc=apply_count, num_elements=num_reviews, progress_interval=args.progress_interval)

        if apply_count != num_reviews:
            print(("ERROR! The vocab mapper ran on %d reviews but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (apply_count, num_reviews))
            return -1
        print("Vocabulary mapping complete!")


if __name__ == '__main__':
    main()
