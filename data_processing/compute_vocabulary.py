from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import json
import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processing.utils import apply_over_generator


def count_vocab(review, acc):
    text = review['text']


def main():
    def restricted_int(x):
        x = int(x)
        if x<1:
            raise argparse.ArgumentTypeError("%r not in range [1,inf)" % (x,))
        return x

    parser = argparse.ArgumentParser(
        description="Constructs a vocabulary and associated frequency count from the tokenized reviews.")
    parser.add_argument(
        'review_path',
        help="The location of json file of reviews to clean",
        type=str)
    parser.add_argument(
        'vocab_path',
        help="The location to save the vocabulary to",
        type=str)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=restricted_int,
        default=5)
    parser.add_argument(
        '--threshold',
        metavar='secs',
        help="The minimum number of times a word can occur without getting mapped to the <UNKNOWN> token",
        type=restricted_int,
        default=10)
    args = parser.parse_args()

    directory = os.path.dirname(args.clean_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.review_path, 'r') as review_file, open(args.vocab_path, 'x+') as vocab_file:
        print("Beginning Filtering!")
        num_reviews = sum(1 for _ in review_file)
        print("There are %d reviews." % num_reviews)
        review_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in review_file)

        num_counted = 0
        vocab_dict = {}
        acc = (num_counted, vocab_dict)
        filtered_count = apply_over_generator(
            reviews, count_vocab, acc=acc, num_elements=num_reviews, progress_interval=args.progress_interval)

        vocab_file.seek(0)
        num_reviews = sum(1 for _ in vocab_file)
        if filtered_count != num_reviews:
            print(("ERROR! The filtered review count was %d but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (filtered_count, num_reviews))
            return -1
        print("After filtering, there are %d reviews." % num_reviews)
        print("Filtering Complete!")


if __name__ == '__main__':
    main()
