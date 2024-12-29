#!/usr/bin/env python
import pandas as pd
from paretoset import paretoset
import re

hdd_size_regex = r'^([\.\d]+) (TB|GB)$'
hdd_rotations_regex = r'^(\d+) rpm$'

hdd_objectives = ['price', 'total capacity', 'rotations', 'Serial ATA']
hdd_objectives_sense = ['min', 'max', 'max', 'diff']


def extract_capacity_scalar(size_str):
    match = re.match(hdd_size_regex, size_str)
    if match:
        size = float(match.group(1))
        unit = match.group(2)
        if unit == 'GB':
            size_tb = size / 1024
        else:
            size_tb = size
        return size_tb
    else:
        raise ValueError(f"Total capacity '{size_str}' does not match the required format.")


def extract_rotations_scalar(rotations_str):
    match = re.match(hdd_rotations_regex, rotations_str)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"Rotations '{rotations_str}' does not match the required format.")


hdd_df = pd.read_csv('data/hdd.csv')

# Clean missing entries
hdd_df = hdd_df.dropna()
hdd_df = hdd_df[hdd_df['rotations'] != 'IntelliPower']
# hdd_df = hdd_df[hdd_df['CL'] != '-']

hdd_df['total capacity'] = hdd_df['total capacity'].apply(extract_capacity_scalar)
hdd_df['rotations'] = hdd_df['rotations'].apply(extract_rotations_scalar)
hdd_df['price per TB'] = hdd_df['price'] / hdd_df['total capacity']

# Filter DDR and DIMM standards
# hdd_df = hdd_df[(hdd_df['ddr'] == 'DDR4') | (hdd_df['ddr'] == 'DDR5')]
# hdd_df = hdd_df[(hdd_df['dimm'] == 'DIMM') | (hdd_df['dimm'] == 'UDIMM')]

hdd_objectives_df = hdd_df[hdd_objectives]
hdd_pareto_mask = paretoset(hdd_df[hdd_objectives], sense=hdd_objectives_sense)
hdd_df[hdd_pareto_mask].to_csv('data/hdd_pareto.csv', index=False)
