from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from time import time


def apply_over_generator(generator, fn, acc=None, num_elements=None, progress_interval=5, start_stop_info=True):
    if start_stop_info:
        print("Applying function...")
    last_time = time()
    last_i = 0
    for i, review in enumerate(generator):
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
