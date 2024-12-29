#!/usr/bin/env python
from util import filter_dataframe
import pandas as pd
from paretoset import paretoset
import re

psu_power_regex = r'^(\d+) W$'
psu_noise_level_regex = r'^(\d+\.?\d*)dBA$'

psu_objectives = ['price', 'power', 'max noise level']
psu_objectives_sense = ['min', 'max', 'min']


def extract_power(power_str):
    match = re.search(psu_power_regex, str(power_str))
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Power string '{power_str}' does not match the required format.")


def extract_noise_level(noise_level_str):
    match = re.search(psu_noise_level_regex, str(noise_level_str))
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"Noise level string '{noise_level_str}' does not match the required format.")


psu_df = pd.read_csv('data/psu.csv')

# Clean incomplete entries
psu_df = filter_dataframe(psu_df, psu_df['max noise level'].notna() & (psu_df['max noise level'] != '-'), 'max noise level present')

# Parse feature values
psu_df['power'] = psu_df['power'].apply(extract_power)
psu_df['max noise level'] = psu_df['max noise level'].apply(extract_noise_level)

# Find Pareto front
psu_objectives_df = psu_df[psu_objectives]
psu_pareto_mask = paretoset(psu_df[psu_objectives], sense=psu_objectives_sense)
psu_df = filter_dataframe(psu_df, psu_pareto_mask, 'Pareto front')

# Apply filters
psu_df = filter_dataframe(psu_df, psu_df['color'] == 'black', 'black color')
psu_df = filter_dataframe(psu_df, psu_df['form factor'] == 'ATX', 'ATX form factor')

# Export
psu_df.to_csv('data/psu_pareto.csv', index=False)
