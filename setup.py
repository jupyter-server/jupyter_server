from setuptools import setup

try:
    from jupyter_packaging import npm_builder, wrap_installers

    ensured_targets = ["jupyter_server/static/style/bootstrap.min.css"]
    cmdclass = wrap_installers(pre_develop=npm_builder(), ensured_targets=ensured_targets)
except ImportError:
    cmdclass = {}

setup(cmdclass=cmdclass)
