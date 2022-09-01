import json
import os
import pathlib
from datetime import datetime, timezone
from uuid import UUID

from jupyter_scheduling.models import CreateJob
from nbformat import NotebookNode


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


def timestamp_to_int(timestamp: str):
    """Converts string date in format yyyy-mm-dd h:m:s to int"""

    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())


def create_output_filename(input_uri: str):
    """Creates output filename from input_uri"""

    filename = os.path.basename(input_uri)
    file_extension = pathlib.Path(input_uri).suffix
    output_filename = f"{os.path.splitext(filename)[0]}-{datetime.now().strftime('%Y%m%d_%I%M%S_%p')}{file_extension}"

    return output_filename


def find_cell_index_with_tag(nb: NotebookNode, tag: str):
    """Finds index of first cell tagged with ``tag``"""

    parameters_indices = []
    for idx, cell in enumerate(nb.cells):
        if "tags" in cell.metadata and tag in cell.metadata["tags"]:
            parameters_indices.append(idx)
    if not parameters_indices:
        return -1
    return parameters_indices[0]


def resolve_path(path, root_dir=None):
    if not root_dir:
        return path

    if "~" in root_dir:
        root_dir = root_dir.replace("~", os.environ["HOME"])

    return os.path.join(root_dir, path)


def get_utc_timestamp() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)
