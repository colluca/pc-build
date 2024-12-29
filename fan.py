#!/usr/bin/env python
from util import filter_dataframe
import pandas as pd
from paretoset import paretoset
import re

fan_features_regex = r'pack of (\d+)|(\d+)x'
fan_loudness_regex = r'^(\d+\.?\d*)'

fan_objectives = ['price per fan', 'loudness', 'width']
fan_objectives_sense = ['min', 'min', 'diff']


def extract_num_fans(features_str):
    if features_str:
        match = re.search(fan_features_regex, str(features_str))
        if match:
            return int(match.group(1) or match.group(2))
    return 1


def extract_loudness(loudness_str):
    match = re.match(fan_loudness_regex, loudness_str)
    if match:
        return float(match.group(1))
    else:
        return 1


fan_df = pd.read_csv('data/fan.csv')

# Clean incomplete entries
fan_df = filter_dataframe(fan_df, fan_df['loudness'].notna(), 'loudness present')

# Parse feature values
# TODO why is width feature missing for fans which do have it on website?
fan_df['number of fans'] = fan_df['features'].apply(extract_num_fans)
fan_df['loudness'] = fan_df['loudness'].apply(extract_loudness)
fan_df['price per fan'] = fan_df['price'] / fan_df['number of fans']

# Find Pareto front
fan_objectives_df = fan_df[fan_objectives]
fan_pareto_mask = paretoset(fan_df[fan_objectives], sense=fan_objectives_sense)
fan_df = filter_dataframe(fan_df, fan_pareto_mask, 'Pareto front')

# Export
fan_df.to_csv('data/fan_pareto.csv', index=False)
