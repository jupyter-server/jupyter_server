"""Migrate jupyter_server configuration.

This splits configuration that belongs in the ServerApp
from the NotebookApp configuration.
"""

import re
import os
import shutil

from traitlets.log import get_logger
from ipython_genutils.text import wrap_paragraphs

from jupyter_core.application import JupyterApp
from jupyter_core.utils import ensure_dir_exists
from jupyter_core.paths import jupyter_config_dir

from jupyter_server.serverapp import ServerApp
from notebook.notebookapp import NotebookApp

pjoin = os.path.join

# Regular expression to strip out notebook traits.
trait_regex = r"\.(?P<trait>[\w]+)[\s]*=(?P<value>[^\n]+)"

# Build a regular expression for services in ServerApp.
classes = {cls.__name__: cls for cls in ServerApp.classes}
classes["NotebookApp"] = NotebookApp
classes["ServerApp"] = ServerApp
classes_regex = re.compile(
    r"(?P<cls>{}){}".format("|".join(classes.keys()), trait_regex)
)


def block_comment(s):
    """return a commented, wrapped block."""
    s = '\n\n'.join(wrap_paragraphs(s, 78))
    return '# ' + s.replace('\n', '\n# ')


def read_configured_traits(config_file):
    traits = []
    with open(config_file, 'r') as f:
        for line in f.readlines():
            line = line.lstrip()
            # Search for lines that are not commented.
            if not line.startswith('#'):
                # Search for NotebookApp traits.
                match = classes_regex.search(line)
                if match:
                    data = match.groupdict()
                    traits.append((data['cls'], data['trait'], data['value']))
    return traits


def sort_configured_traits(traits):
    """Sort """
    server_trait_names = ServerApp.class_trait_names()
    server_traits, notebook_traits = [], []
    for trait in traits:
        cls, name, value = trait
        if cls == "NotebookApp":
            if name in server_trait_names:
                server_traits.append(("ServerApp", name, value))
            else:
                notebook_traits.append("NotebookApp", name, value)
        elif cls in classes: 
            server_traits.append(trait)
        else:
            notebook_traits.append(trait)
    return server_traits, notebook_traits


def write_migrated_config(traits):
    """Build migrate config text for given app."""
    lines = [
        '#'+'-'*78,
        '# Migrated from NotebookApp (<notebook 5.0.0) configuration',
        '#'+'-'*78+'\n',
    ]
    for cls, name, value in traits:
        trait = getattr(classes[cls], name)
        trait_str = "c.{}.{} ={}\n".format(cls, name, value)
        lines.append(block_comment(trait.help))
        lines.append(trait_str)
    return '\n'.join(lines)


def migrate_config(src, server_dst, notebook_dst):
    """Separate NotebookApp configuration from ServerApp configuration.
    """
    traits = read_configured_traits(src)
    server_traits, notebook_traits = sort_configured_traits(traits)

    server_cfg = write_migrated_config(server_traits)
    notebook_cfg = write_migrated_config(notebook_traits)

    server_cfg += ServerApp.class_config_section()
    notebook_cfg += NotebookApp.class_config_section()

    # Append '_migrated' to src file.
    head, tail = os.path.splitext(src)
    shutil.move(src, head+"_migrated"+tail)

    # Write server config
    with open(server_dst, 'w') as f:
        f.write(server_cfg)

    # Write notebook config
    with open(notebook_dst, 'w') as f:
        f.write(notebook_cfg)

    migrated = True
    return migrated

def migrate():
    migrated = False
    # Home directory
    src = pjoin(jupyter_config_dir(), 'jupyter_notebook_config.py')
    server_dst = pjoin(jupyter_config_dir(), 'jupyter_server_config.py')
    notebook_dst = pjoin(jupyter_config_dir(), 'jupyter_notebook_config.py')

    if os.path.exists(server_dst) and os.path.exists(notebook_dst):
        print("Configuration already migrated?")
        migrated = True
    else:
        migrate_config(src, server_dst, notebook_dst)
        migrated = True

    return migrated


class JupyterServerMigrate(JupyterApp):
    name = 'jupyter-server-migrate'
    description = """
    Migrate Notebook server configuration to Jupyter Server.
    """

    def start(self):
        if not migrate():
            self.log.info("Found nothing to migrate.")


main = JupyterServerMigrate.launch_instance

if __name__ == '__main__':
    main()
