"""Utility module"""
import math


def sec_to_hour(SEC):
    SEC = math.floor(SEC)
    MIN = math.floor(SEC / 60)
    HOUR = math.floor(MIN / 60)
    MIN = MIN % 60
    SEC = SEC % 60
    return "{:02d}:{:02d}:{:02d}".format(HOUR, MIN, SEC)
