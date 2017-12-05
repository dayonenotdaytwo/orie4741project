from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))

import json
import argparse

from operator import itemgetter
from functools import partial
from data_processing.utils import apply_over_generator, restricted_float, restricted_int


def review_parse(ratio, threshold, cleaned_file, review, acc):
    u = review['useful']
    f = review['funny']
    c = review['cool']
    total_compliments = u + f + c
    index, value = max(enumerate((u, f, c)), key=itemgetter(1))  # argmax with value, key
    if total_compliments <= threshold or value / total_compliments <= ratio:  # Filter out reviews
        return acc
    review['max_compliment_type'] = ('useful', 'funny', 'cool')[index]
    json.dump(review, cleaned_file)
    cleaned_file.write('\n')
    return acc+1


def main():
    parser = argparse.ArgumentParser(
        description="Filters the reviews by proportion of highest compliment type to total, " +
                    "and by minimum compliments received.")
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
        type=restricted_int,
        default=5)
    parser.add_argument(
        '--threshold',
        metavar='n',
        help="The minimum number of compliments received",
        type=restricted_int,
        default=10)
    parser.add_argument(
        '--ratio',
        metavar='r',
        help="The minimum ratio of the highest compliment category to the total number of compliments",
        type=restricted_float,
        default=0.5)
    args = parser.parse_args()

    directory = os.path.dirname(args.clean_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.dirty_path, 'r') as dirty_file, open(args.clean_path, 'x+') as cleaned_file:
        print("Beginning filtering!")
        num_reviews = sum(1 for _ in dirty_file)
        print("There are %d reviews." % num_reviews)
        dirty_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in dirty_file)

        fn = partial(review_parse, args.ratio, args.threshold, cleaned_file)
        filtered_count = 0
        filtered_count = apply_over_generator(reviews, fn, acc=filtered_count, num_elements=num_reviews)

        # Count remaining reviews
        cleaned_file.seek(0)
        num_reviews = sum(1 for _ in cleaned_file)
        if filtered_count != num_reviews:
            print(("ERROR! The filtered review count was %d but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (filtered_count, num_reviews))
            return -1
        print("After filtering, there are %d reviews." % num_reviews)
        print("Filtering complete!")


if __name__ == '__main__':
    main()
