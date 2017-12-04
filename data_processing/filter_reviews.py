from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import json
import argparse
import os

from operator import itemgetter
from data_processing.utils import apply_over_generator
from functools import partial


def review_parse(ratio, threshold, cleaned_file, review, acc):
    u = review['useful']
    f = review['funny']
    c = review['cool']
    total_compliments = u + f + c
    index, value = max(enumerate((u, f, c)), key=itemgetter(1))  # argmax with value, key
    if total_compliments < threshold or value / total_compliments < ratio:  # Filter out reviews
        return acc
    review['max_compliment_type'] = ('useful', 'funny', 'cool')[index]
    json.dump(review, cleaned_file)
    cleaned_file.write('\n')
    return acc+1


def main():
    def restricted_float(x):
        """Constrcts a float. Throws exception if outside of [0,1].

        From https://stackoverflow.com/questions/12116685/how-can-i-require-my-python-scripts-argument-to-be-a-float-between-0-0-1-0-usin
        """
        x = float(x)
        if x < 0.0 or x > 1.0:
            raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]" % (x,))
        return x

    def restricted_int(x):
        x = int(x)
        if x<1:
            raise argparse.ArgumentTypeError("%r not in range [1,inf)" % (x,))
        return x

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
        metavar='secs',
        help="The minimum number of compliments received",
        type=restricted_int,
        default=10)
    parser.add_argument(
        '--ratio',
        metavar='r',
        help="The minimum ratio of the highest compliment category to the total number of compliments",
        type=restricted_float,
        default=0.4)
    args = parser.parse_args()

    directory = os.path.dirname(args.clean_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(args.dirty_path, 'r') as dirty_file, open(args.clean_path, 'x+') as cleaned_file:
        print("Beginning Filtering!")
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
        print("Filtering Complete!")


if __name__ == '__main__':
    main()
