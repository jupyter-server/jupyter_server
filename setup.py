import subprocess
import sys

from setuptools import setup

try:
    from jupyter_packaging import npm_builder, wrap_installers

    ensured_targets = ["jupyter_server/static/style/bootstrap.min.css"]

    def post_develop(*args, **kwargs):
        npm_builder()
        try:
            subprocess.run([sys.executable, "-m", "pre_commit", "install"])
            subprocess.run(
                [sys.executable, "-m", "pre_commit", "install", "--hook-type", "pre-push"]
            )
        except Exception:
            pass

    cmdclass = wrap_installers(post_develop=post_develop, ensured_targets=ensured_targets)
except ImportError:
    cmdclass = {}

setup(cmdclass=cmdclass)
