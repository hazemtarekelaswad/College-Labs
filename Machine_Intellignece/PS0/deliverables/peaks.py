from typing import List
import utils

def peaks(seq: List[int]) -> int:
    '''
    This function takes sequence of integers and returns the number of peaks.
    A peak is an element in the sequence whose value is higher than the two elements surrounding it.
    The first and last elements cannot be peaks.
    Any list containing less than 3 elements will have 0 peaks. 
    '''
    #TODO: ADD YOUR CODE HERE
    if len(seq) <= 2: return 0
    count = 0
    for i in range(1, len(seq) - 1):
        count += seq[i - 1] < seq[i] > seq[i + 1]
    return count 