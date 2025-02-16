#!/usr/bin/env python
import pandas as pd
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


mobo_df = pd.read_csv('data/complete/mobo.csv')

# Clean missing entries
mobo_df = mobo_df.dropna()
# mobo_df = mobo_df[mobo_df['CL'] != '-']

# Rename features
# mobo_df.rename({'other': 'NVMe'})

# Process feature values
mobo_df['M.2'] = mobo_df['M.2'].apply(extract_m2_count)
mobo_df['number of slots'] = mobo_df['number of slots'].apply(int)
mobo_df['SATA 6Gb/s'] = mobo_df['SATA 6Gb/s'].apply(extract_sata_count)
# mobo_df['frequency'] = mobo_df['frequency'].apply(extract_frequency_scalar)
# mobo_df['latency'] = mobo_df['CL'].apply(extract_latency_scalar)

# Filter mobos with AM5 socket, more than 4 RAM slots, more than 2 M.2 slots
mobo_df = mobo_df[mobo_df['socket'] == 'AMD socket AM5']
mobo_df = mobo_df[mobo_df['number of slots'] >= 4]
mobo_df = mobo_df[mobo_df['M.2'] >= 2]
mobo_df = mobo_df[mobo_df['SATA 6Gb/s'] >= 4]

# Sort by price
mobo_df.sort_values('price', ascending=True, inplace=True)

# Export filtered mobos
mobo_df.to_csv('data/filtered/mobo.csv', index=False)
