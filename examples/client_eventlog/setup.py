# Adapted from https://github.com/jasongrout/jupyter_core/blob/0310f4a199ba7da60abc54bd9115f7da9a9cec25/examples/scale/template/setup.py # noqa
from setuptools import setup

name = 'client_eventlog'

setup(
  name=name,
  version="1.0.0",
  packages=[name],
  include_package_data=True,
  entry_points= {
    'jupyter_telemetry': [
      f'{name}.sample_entry_point = {name}:JUPYTER_TELEMETRY_SCHEMAS'
    ]
  }
)
