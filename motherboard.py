#!/usr/bin/env python
import pandas as pd
from paretoset import paretoset
import re

m2_count_regex = r'^(\d+)x M\.2'
sata_count_regex = r'^(\d+)x$'


def extract_m2_count(m2_str):
    match = re.match(m2_count_regex, m2_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"M.2 string '{m2_str}' does not match the required format.")


def extract_sata_count(sata_str):
    match = re.match(sata_count_regex, sata_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"SATA string '{sata_str}' does not match the required format.")


motherboard_df = pd.read_csv('data/motherboard.csv')

# Clean missing entries
# motherboard_df = motherboard_df.dropna()
# motherboard_df = motherboard_df[motherboard_df['CL'] != '-']

# Rename features
# motherboard_df.rename({'other': 'NVMe'})

# Process feature values
motherboard_df['M.2'] = motherboard_df['M.2'].apply(extract_m2_count)
motherboard_df['number of slots'] = motherboard_df['number of slots'].apply(int)
motherboard_df['SATA 6Gb/s'] = motherboard_df['SATA 6Gb/s'].apply(extract_sata_count)
# motherboard_df['frequency'] = motherboard_df['frequency'].apply(extract_frequency_scalar)
# motherboard_df['latency'] = motherboard_df['CL'].apply(extract_latency_scalar)

# Filter motherboards with AM5 socket, more than 4 RAM slots, more than 2 M.2 slots
motherboard_df = motherboard_df[motherboard_df['socket'] == 'AMD socket AM5']
motherboard_df = motherboard_df[motherboard_df['number of slots'] >= 4]
motherboard_df = motherboard_df[motherboard_df['M.2'] >= 2]
motherboard_df = motherboard_df[motherboard_df['SATA 6Gb/s'] >= 4]

# Filter Pareto-optimal motherboards
# motherboard_objectives_df = motherboard_df[motherboard_objectives]
# motherboard_pareto_mask = paretoset(motherboard_df[motherboard_objectives], sense=motherboard_objectives_sense)
# motherboard_df = motherboard_df[motherboard_pareto_mask]

# Export filtered motherboards
motherboard_df.to_csv('data/motherboard_pareto.csv', index=False)
