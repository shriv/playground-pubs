
import pandas as pd
import numpy as np

# MOVE TO UTILS
# Conversion functions
def hiking_speed(grade, params_list):
    W = params_list[0]*np.exp(- params_list[1]* np.abs(grade + params_list[2]))
    return W

def flat_travel_time(distance, speed=5.0):
    time_hr = (distance / 1000) / speed
    time_mins = time_hr * 60.0
    return time_mins

def hiking_time(grade, distance, params_list):
    W = params_list[0]*np.exp(- params_list[1]* np.abs(grade + params_list[2]))
    time_hr = (distance / 1000) / W
    time_mins = time_hr * 60.0
    return time_mins
