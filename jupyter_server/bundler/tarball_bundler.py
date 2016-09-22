# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import io
import tarfile
import nbformat

def _jupyter_bundlerextension_paths():
    """Metadata for notebook bundlerextension"""
    return [{
        # unique bundler name
        "name": "tarball_bundler",
        # module containing bundle function
        "module_name": "jupyter_server.bundler.tarball_bundler",
        # human-redable menu item label
        "label" : "Notebook Tarball (tar.gz)",
        # group under 'deploy' or 'download' menu
        "group" : "download",
    }]

def bundle(handler, model):
    """Create a compressed tarball containing the document.
    
    Parameters
    ----------
    handler : tornado.web.RequestHandler
        Handler that serviced the bundle request
    model : dict
        Notebook model from the configured ContentManager
    """
    notebook_filename = model['name']
    notebook_content = nbformat.writes(model['content']).encode('utf-8')
    notebook_name = os.path.splitext(notebook_filename)[0]
    tar_filename = '{}.tar.gz'.format(notebook_name)
    
    info = tarfile.TarInfo(notebook_filename)
    info.size = len(notebook_content)

    with io.BytesIO() as tar_buffer:
        with tarfile.open(tar_filename, "w:gz", fileobj=tar_buffer) as tar:
            tar.addfile(info, io.BytesIO(notebook_content))
        
        handler.set_header('Content-Disposition',
                           'attachment; filename="{}"'.format(tar_filename))
        handler.set_header('Content-Type', 'application/gzip')
                
        # Return the buffer value as the response
        handler.finish(tar_buffer.getvalue())
