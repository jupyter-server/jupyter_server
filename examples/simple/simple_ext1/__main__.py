from traitlets import Dict

from jupyter_server.serverapp import launch_new_instance, ServerApp

if __name__ is '__main__':
    ServerApp.jpserver_extensions = Dict({'simple_ext1': True})
    launch_new_instance()
