from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import argparse
from time import time


def apply_over_generator(iterable, fn, acc=None, num_elements=None, progress_interval=5, start_stop_info=True):
    """Apply a function to the contents of an iterable. Can also print progress of application.

    Args:
        iterable:  An iterable to apply the function to.
        fn:  The function to apply.
        acc:  An accumulator variable for `fn`.
        num_elements:  The number of elements in the iterable. If `None`, no progress can be printed.
        progress_interval:  The interval in seconds to wait before printing updated progress.
        start_stop_info:  Whether or not to print messages when starting and stopping the function application.

    Returns:
        The updated value of `acc`.
    """
    if start_stop_info:
        print("Applying function...")
    last_time = time()
    last_i = 0
    for i, review in enumerate(iterable):
        acc = fn(review, acc)
        if num_elements is not None:
            current_time = time()
            delta = current_time - last_time
            if delta >= progress_interval:
                if num_elements is not None:
                    average_speed = (i - last_i) / delta
                    est_time_remaining = (num_elements - i) / average_speed
                    last_i = i
                    print("Percent Complete: %7.4f, Est. Minutes Remaining: %6.1f" %
                          (i / num_elements * 100, est_time_remaining / 60))
                last_time = current_time
    if start_stop_info:
        print("Function application completed!")
    return acc


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
