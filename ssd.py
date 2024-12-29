#!/usr/bin/env python
import pandas as pd
from paretoset import paretoset
import re

ssd_size_regex = r'^([\.\d]+) (TB|GB)$'
ssd_speed_regex = r'^([\.\d]+) (GB|MB)/s$'

ssd_objectives = ['price', 'total capacity', 'reading speed (SSD)', 'writing speed (SSD)']
ssd_objectives_sense = ['min', 'max', 'max', 'max']


def extract_capacity_scalar(size_str):
    match = re.match(ssd_size_regex, size_str)
    if match:
        size = float(match.group(1))
        unit = match.group(2)
        if unit == 'TB':
            size_gb = size * 1024
        else:
            size_gb = size
        return size_gb
    else:
        raise ValueError(f"Total capacity '{size_str}' does not match the required format.")


def extract_speed_scalar(speed_str):
    match = re.match(ssd_speed_regex, speed_str)
    if match:
        speed = float(match.group(1))
        unit = match.group(2)
        if unit == 'GB':
            speed_mb = speed * 1024
        else:
            speed_mb = speed
        return speed_mb
    else:
        raise ValueError(f"Speed '{speed_str}' does not match the required format.")


ssd_df = pd.read_csv('data/ssd.csv')

# Clean missing entries
ssd_df = ssd_df.dropna()
ssd_df = ssd_df[ssd_df['reading speed (SSD)'] != '-']
ssd_df = ssd_df[ssd_df['writing speed (SSD)'] != '-']

ssd_df['total capacity'] = ssd_df['total capacity'].apply(extract_capacity_scalar)
ssd_df['reading speed (SSD)'] = ssd_df['reading speed (SSD)'].apply(extract_speed_scalar)
ssd_df['writing speed (SSD)'] = ssd_df['writing speed (SSD)'].apply(extract_speed_scalar)
ssd_df['price per TB'] = 1000 * ssd_df['price'] / ssd_df['total capacity']

# Filter form factor
ssd_df = ssd_df[ssd_df['size'] == 'M.2 (2280)']

# Find Pareto front
ssd_objectives_df = ssd_df[ssd_objectives]
ssd_pareto_mask = paretoset(ssd_df[ssd_objectives], sense=ssd_objectives_sense)
ssd_df = ssd_df[ssd_pareto_mask]

# Export
ssd_df.to_csv('data/ssd_pareto.csv', index=False)
