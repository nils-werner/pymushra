import fnmatch
import os
from io import BytesIO, StringIO



def get_configs(path):
    """Retrieves all config files from webMUSHRA config directory"""
    return [file for file in os.listdir(path) if fnmatch.fnmatch(file, "*.yaml")]


def flatten_columns(columns):
    """Transforms hierarchical column names to concatenated single-level
    columns

    """
    return ["_".join(col).strip() for col in columns]


def to_bytesio(data: BytesIO | StringIO) -> BytesIO:
    if isinstance(data, BytesIO):
        return data

    out = BytesIO()
    out.write(data.getvalue().encode("utf-8"))
    out.seek(0)
    return out
