#!/usr/bin/env python
from util import filter_dataframe
import pandas as pd
import re

case_drives_regex = r'^(\d+)x$'


def extract_num_drives(drives_str):
    match = re.match(case_drives_regex, drives_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Drives '{drives_str}' does not match the required format.")


case_df = pd.read_csv('data/case.csv')

# Clean incomplete entries
case_df = case_df.dropna()
case_df = filter_dataframe(case_df, case_df['internal 3.5"'] != '-', 'number of drives present')

# Parse feature values
case_df['internal 3.5"'] = case_df['internal 3.5"'].apply(extract_num_drives)

# Filter form factor and number of drives
case_df = filter_dataframe(case_df, (case_df['max. form factor'] == 'E-ATX') | (case_df['max. form factor'] == 'ATX'), 'minimum motherboard size')
case_df = filter_dataframe(case_df, case_df['internal 3.5"'] >= 4, 'minimum number of 3.5" drives')
case_df = filter_dataframe(case_df, case_df['type'] == 'tower case', 'case type')
case_df = filter_dataframe(case_df, case_df['color'].str.contains('black'), 'black color')

# Export
case_df.to_csv('data/case_pareto.csv', index=False)
