import os
import fnmatch


def get_configs(path):
    """ Retrieves all config files from webMUSHRA config directory

    """
    return [
        file for file in os.listdir(path) if fnmatch.fnmatch(file, "*.yaml")
    ]


def flatten_columns(columns):
    """ Transforms hierarchical column names to concatenated single-level
    columns

    """
    return ['_'.join(col).strip() for col in columns]
