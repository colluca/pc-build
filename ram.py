#!/usr/bin/env python
import pandas as pd
from paretoset import paretoset
import re

ram_size_regex = r'^(\d+) (MB|GB)$'
ram_ddr_dimm_regex = r'^(DDR\d*)-([A-Z-]+)$'
ram_freq_regex = r'^.+ \((\d+)(MHz|Mhz)\)$'
ram_latency_regex = r'^CL(\d+)'

ram_objectives = ['price', 'number of modules', 'module size', 'frequency', 'ddr', 'latency']
ram_objectives_sense = ['min', 'diff', 'max', 'max', 'diff', 'min']


def extract_size_scalar(size_str):
    match = re.match(ram_size_regex, size_str)
    if match:
        size = float(match.group(1))
        unit = match.group(2)
        if unit == 'MB':
            size_gb = size / 1024
        else:
            size_gb = size
        return size_gb
    else:
        raise ValueError(f"Module size '{size_str}' does not match the required format.")


def extract_ddr_type(type_str):
    match = re.match(ram_ddr_dimm_regex, type_str)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Type string '{type_str}' does not match the required format.")


def extract_dimm_type(type_str):
    match = re.match(ram_ddr_dimm_regex, type_str)
    if match:
        return match.group(2)
    else:
        raise ValueError(f"Type string '{type_str}' does not match the required format.")


def extract_frequency_scalar(frequency_str):
    match = re.match(ram_freq_regex, frequency_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Frequency string '{frequency_str}' does not match the required format.")


def extract_latency_scalar(cl_str):
    match = re.match(ram_latency_regex, cl_str)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"CL string '{cl_str}' does not match the required format.")


ram_df = pd.read_csv('data/complete/ram.csv')

# Clean missing entries
ram_df = ram_df.dropna()
ram_df = ram_df[ram_df['CL'] != '-']

ram_df['module size'] = ram_df['module size'].apply(extract_size_scalar)
ram_df['ddr'] = ram_df['type'].apply(extract_ddr_type)
ram_df['dimm'] = ram_df['type'].apply(extract_dimm_type)
ram_df['frequency'] = ram_df['frequency'].apply(extract_frequency_scalar)
ram_df['latency'] = ram_df['CL'].apply(extract_latency_scalar)
ram_df['number of modules'] = ram_df['number of modules'].apply(int)
ram_df['total capacity'] = ram_df['module size'] * ram_df['number of modules']
ram_df['price per GB'] = ram_df['price'] / ram_df['total capacity']
ram_df['price per GT/s'] = 1000 * ram_df['price'] / ram_df['frequency']

# Filter DDR and DIMM standards
ram_df = ram_df[ram_df['ddr'] == 'DDR5']
ram_df = ram_df[(ram_df['dimm'] == 'DIMM') | (ram_df['dimm'] == 'UDIMM')]

# Find Pareto front
ram_objectives_df = ram_df[ram_objectives]
ram_pareto_mask = paretoset(ram_df[ram_objectives], sense=ram_objectives_sense)
ram_df = ram_df[ram_pareto_mask]

# Filter number of modules
ram_df = ram_df[ram_df['number of modules'] == 2]

# Sort by price per GB
ram_df.sort_values('price per GB', ascending=True, inplace=True)

# Export
ram_df.to_csv('data/filtered/ram.csv', index=False)
