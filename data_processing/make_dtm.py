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


def put_in_matrix(vocab_list, dtm, review, row_num):
    for sentence in review['text']:
        for word in sentence:
            try:
                idx = vocab_list.index(word)
                dtm[row_num, idx] += 1
            except ValueError:
                continue
    return row_num+1


def main():
    parser = argparse.ArgumentParser(
        description="Constructs a document-term-matrix from the tokenized reviews and a vocabulary.")
    parser.add_argument(
        'review_path',
        help="The location of json file of reviews to make the matrix from",
        type=str)
    parser.add_argument(
        'vocab_pickle',
        help="The location of the vocabulary pickle file",
        type=str)
    parser.add_argument(
        'dtm_path',
        help="The location of DTM to save to",
        type=str)
    parser.add_argument(
        '--top_n_words',
        metavar='N',
        default=128,
        help='The number of most frequent words to select',
        type=restricted_int)
    parser.add_argument(
        '--progress_interval',
        metavar='secs',
        help="The progress printing interval in seconds",
        type=restricted_int,
        default=5)
    args = parser.parse_args()

    if os.path.exists(args.dtm_path):
        raise FileExistsError("There is already a file at %s! Please move it and try again." % args.dtm_path)

    with open(args.review_path, 'r') as review_file, open(args.vocab_pickle, 'rb') as vocab_pickle:
        print("Beginning DTM construction!")
        num_reviews = sum(1 for _ in review_file)
        print("There are %d reviews." % num_reviews)

        vocab_dict = pickle.load(vocab_pickle)
        num_words = len(vocab_dict)
        vocab_list = list(key for key, _ in vocab_dict.items())
        print("There are %d words in the vocabulary." % num_words)

        dtm = np.zeros((num_reviews, args.top_n_words), dtype=np.int32)
        #dtm = np.memmap(args.dtm_path, dtype=np.int16, mode='w+', shape=(num_reviews, num_words))

        review_file.seek(0)  # Reset stream position to start
        reviews = (json.loads(line) for line in review_file)

        fn = partial(put_in_matrix, vocab_list[:args.top_n_words], dtm)
        apply_count = 0
        apply_count = apply_over_generator(
            reviews, fn, acc=apply_count, num_elements=num_reviews, progress_interval=args.progress_interval)

        if apply_count != num_reviews:
            print(("ERROR! The dtm constructor ran on %d reviews but the number of reviews in the file is %d. " +
                  "They should match! Something went wrong.") % (apply_count, num_reviews))
            return -1
        np.save(args.dtm_path, dtm)
        #del dtm  # Flush the matrix to disk and close it
        print("DTM construction complete!")


if __name__ == '__main__':
    main()
