from traitlets import Dict

from jupyter_server.serverapp import ServerApp

if __name__ is '__main__':
    ServerApp.jpserver_extensions = Dict({
        'simple_ext1': True,
        'simple_ext2': True
        })
    ServerApp.launch_instance()
