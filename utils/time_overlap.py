# utils/time_overlap.py

def is_time_overlap(start1, end1, start2, end2):
    return start1 < end2 and end1 > start2
