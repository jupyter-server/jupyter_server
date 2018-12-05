"""
1. Load notebook config
2. Rip out traits in notebook not in 
3. Swap NotebookApp traits with ServerApp Traits.
4. Remove ServerApp traits from NotebookApp.
5. Write NotebookApp config to jupyter_notebook_config.py
6. Write ServerApp config to jupyter_server_config.py

# """

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


def block_comment(s):
    """return a commented, wrapped block."""
    s = '\n\n'.join(wrap_paragraphs(s, 78))
    return '# ' + s.replace('\n', '\n# ')


# Regular expression to strip out notebook traits.
trait_regex = re.compile(
    r"c.NotebookApp\.(?P<trait>[\w]+)[\s]*=(?P<value>[^\n]+)")


def find_traits_in_file(config_file):
    """Search notebook config file for configured traits."""
    found = {}
    with open(config_file, 'r') as f:
        for line in f.readlines():
            line = line.lstrip()
            # Search for lines that are not commented.
            if not line.startswith('#'):
                # Search for NotebookApp traits.
                match = trait_regex.search(line)
                if match:
                    data = match.groupdict()
                    found[data['trait']] = data['value']
    return found


def migrated_app_config(app, traits):
    """Build migrate config text for given app."""
    lines = [
        '#'+'-'*78,
        '# Migrated from NotebookApp (<notebook 5.0.0) configuration',
        '#'+'-'*78+'\n',
    ]
    for name, value in traits.items():
        trait = getattr(ServerApp, name)
        trait_str = "c.{}.{} ={}\n".format(app.__name__, name, value)
        lines.append(block_comment(trait.help))
        lines.append(trait_str)
    lines.append(app.class_config_section())
    return '\n'.join(lines)


def migrate_config(src, server_dst, notebook_dst):
    """Separate NotebookApp configuration from ServerApp configuration.
    """
    # Find configured traits in old jupyter_notebook_config
    found_traits = find_traits_in_file(src)
    found_set = set(found_traits.keys())

    # Traits specific to the ServerApp.
    server_trait_names = found_set.intersection(ServerApp.class_trait_names())
    # Traits specific to the NotebookApp.
    notebook_trait_names = found_set.difference(
        NotebookApp.class_trait_names())

    # Get values of traits from file.
    server_traits = {name: found_traits[name]
                     for name in server_trait_names}
    notebook_traits = {name: found_traits[name]
                       for name in notebook_trait_names}

    # Build config text.
    server_cfg = migrated_app_config(ServerApp, server_traits)
    notebook_cfg = migrated_app_config(NotebookApp, notebook_traits)

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
