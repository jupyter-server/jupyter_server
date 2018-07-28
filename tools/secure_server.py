#!/usr/bin/env python
"""
script to automatically setup server over SSL.

Generate cert and keyfiles (rsa 1024) in ~/.ssh/, ask for a password, and add
the corresponding entries in the JSON configuration file.
"""

import six

from jupyter_server.auth import passwd
from traitlets.config.loader import JSONFileConfigLoader, ConfigFileNotFound
from jupyter_core.paths import jupyter_config_dir
from traitlets.config import Config

from contextlib import contextmanager

from OpenSSL import crypto
from os.path import exists, join

import io
import os
import json
import traceback


def create_self_signed_cert(cert_dir, keyfile, certfile):
    """
    Create a self-signed `keyfile` and `certfile` in `cert_dir`

    Abort if one of the keyfile of certfile exist.
    """

    if exists(join(cert_dir, certfile))  or exists(join(cert_dir, keyfile)):
        raise FileExistsError('{} or {} already exist in {}. Aborting.'.format(keyfile, certfile, cert_dir))
    else:
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "Jupyter Server self-signed certificate"
        cert.get_subject().L = "Jupyter Server self-signed certificate"
        cert.get_subject().O = "Jupyter Server self-signed certificate"
        cert.get_subject().OU = "my organization"
        cert.get_subject().CN = "Jupyter Server self-signed certificate"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        with io.open(join(cert_dir, certfile), "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf8'))
        os.chmod(join(cert_dir, certfile), 0o600)

        with io.open(join(cert_dir, keyfile), "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf8'))
        os.chmod(join(cert_dir, keyfile), 0o600)


@contextmanager
def persist_config(mode=0o600):
    """Context manager that can be use to modify a config object

    On exit of the context manager, the config will be written back to disk,
    by default with 600 permissions.
    """

    loader = JSONFileConfigLoader('jupyter_server_config.json', jupyter_config_dir())
    try:
        config = loader.load_config()
    except ConfigFileNotFound:
        config = Config()

    yield config

    filepath = os.path.join(jupyter_config_dir(), 'jupyter_server_config.json')
    with io.open(filepath, 'w') as f:
        f.write(six.u(json.dumps(config, indent=2)))
    try:
        os.chmod(filepath, mode)
    except Exception:
        traceback.print_exc()

        print("Something went wrong changing file permissions")


def set_password():
    """Ask user for password, store it in json configuration file"""

    print("First choose a password.")
    hashedpw = passwd()
    print("We will store your password encrypted in the server configuration file: ")
    print(hashedpw)

    with persist_config() as config:
        config.ServerApp.password = hashedpw

    print('... done\n')


def set_certifs():
    """
    Generate certificate to run the Jupyter server over SSL and set up the server config.
    """
    print("Let's generate self-signed certificates to secure your connexion.")
    print("where should the certificate live?")

    location = input('path [~/.ssh]: ')
    if not location.strip():
        location = os.path.expanduser('~/.ssh')
    keyfile = input('keyfile name [jupyter_server.key]: ')
    if not keyfile.strip():
        keyfile = 'jupyter_server.key'
    certfile = input('certfile name [jupyter_server.crt]: ')
    if not certfile.strip():
        certfile = 'jupyter_server.crt'

    create_self_signed_cert(location, keyfile, certfile)

    fullkey = os.path.join(location, keyfile)
    fullcrt = os.path.join(location, certfile)
    with persist_config() as config:
        config.ServerApp.certfile = fullcrt
        config.ServerApp.keyfile = fullkey

    print('done.\n')


if __name__ == '__main__':
    print("This will guide you through the steps towards securing your Jupyter server.")
    set_password()
    set_certifs()
