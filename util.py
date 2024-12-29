def filter_dataframe(df, filter, name=None):
    original_size = df.index.size
    filtered_size = filter.sum()
    num_removed = original_size - filtered_size
    print(f'Removed {num_removed}/{original_size} entries by {name + " " if name else ""}filter.')
    return df[filter]
