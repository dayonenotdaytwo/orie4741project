from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os.path as p
sys.path.append(p.abspath(p.dirname(__file__) + '/../'))

import json
import argparse

from data_processing.utils import apply_over_generator


def main():
    def restricted_int(x):
        x = int(x)
        if x < 1:
            raise argparse.ArgumentTypeError("%r not in range [1,inf)" % (x,))
        return x

    parser = argparse.ArgumentParser(
        description="Flattens the nested text lists in a json file.")
    parser.add_argument(
        'nested_path',
        help="The location of the nested json file to clean",
        type=str)
    parser.add_argument(
        'flattened_path',
        help="The location to save the flattened json file to",
        type=str)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=restricted_int,
        default=5)
    args = parser.parse_args()
    flattened_path = args.flattened_path
    nested_path = args.nested_path

    directory = os.path.dirname(flattened_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    def flatten(review, acc):
        lists = review['text']
        flattened = []
        for sentence in lists:
            flattened += sentence
        review['text'] = flattened
        json.dump(review, flattened_file)
        flattened_file.write('\n')
        return acc + 1

    with open(nested_path, 'r') as nested_file, open(flattened_path, 'x+') as flattened_file:
        print("Beginning Filtering!")
        num_reviews = sum(1 for _ in nested_file)
        print("There are %d reviews." % num_reviews)
        nested_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in nested_file)

        fn = flatten
        filtered_count = 0
        filtered_count = apply_over_generator(
            reviews, fn, acc=filtered_count, num_elements=num_reviews, progress_interval=args.progress_interval)

        # Count remaining reviews
        flattened_file.seek(0)
        num_reviews = sum(1 for _ in flattened_file)
        if filtered_count != num_reviews:
            print(("ERROR! The filtered review count was %d but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (filtered_count, num_reviews))
            return -1
        print("After filtering, there are %d reviews." % num_reviews)
        print("Filtering Complete!")


if __name__ == '__main__':
    main()
