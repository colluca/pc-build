#!/usr/bin/env python
import pandas as pd
from paretoset import paretoset
import re

cpu_core_count_regex = r'^(\d+)x$'
cpu_clock_rate_regex = r'^(\d+(\.\d+)?)GHz$'
cpu_cache_size_regex = r'^(\d+)x\s*(\d+(\.\d+)?)(MB|kB)$'

cpu_objectives = ['price', 'performance', 'L2 cache', 'L3 cache']
cpu_objectives_sense = ['min', 'max', 'max', 'max']


def extract_core_count_scalar(core_count_str):
    match = re.match(cpu_core_count_regex, core_count_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Core count '{core_count_str}' does not match the required format.")


def extract_clock_rate_scalar(clock_rate_str):
    match = re.match(cpu_clock_rate_regex, clock_rate_str)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"CPU clock rate '{clock_rate_str}' does not match the required format.")


def extract_total_cache_size(cache_size_str):
    if pd.isna(cache_size_str):
        return 0
    match = re.match(cpu_cache_size_regex, cache_size_str, re.IGNORECASE)
    if match:
        multiplier = int(match.group(1))
        size = float(match.group(2))
        unit = match.group(4).lower()
        if unit == 'mb':
            size_kb = size * 1024
        else:
            size_kb = size
        return multiplier * size_kb
    else:
        raise ValueError(f"CPU cache size '{cache_size_str}' does not match the required format.")


cpu_df = pd.read_csv('data/cpu.csv')

cpu_core_count_scalar = cpu_df['CPU cores'].apply(extract_core_count_scalar)
cpu_clock_rate_scalar = cpu_df['clock rate'].apply(extract_clock_rate_scalar)
cpu_df['performance'] = cpu_core_count_scalar * cpu_clock_rate_scalar
cpu_df['L2 cache'] = cpu_df['L2 cache'].apply(extract_total_cache_size)
cpu_df['L3 cache'] = cpu_df['L3 cache'].apply(extract_total_cache_size)
cpu_df['performance per dollar [MOPS/$]'] = 1000 * cpu_df['performance'] / cpu_df['price']
cpu_df['L3 per dollar [KB/$]'] = cpu_df['L3 cache'] / cpu_df['price']

cpu_objectives_df = cpu_df[cpu_objectives]
cpu_pareto_mask = paretoset(cpu_df[cpu_objectives], sense=cpu_objectives_sense)
cpu_df[cpu_pareto_mask].to_csv('data/cpu_pareto.csv', index=False)
