from traitlets import Dict

from jupyter_server.serverapp import ServerApp

if __name__ is '__main__':
    ServerApp.jpserver_extensions = Dict({
        'simple_ext1': False,
        'simple_ext2': False,
        'simple_ext11': True,
        })
    ServerApp.launch_instance()
