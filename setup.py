import os
from setuptools import Command, setup

"""
Setup script.
Template python setup script
"""


class CleanCommand(Command):
  """Source - https://stackoverflow.com/a/3780822
  Posted by jathanism, modified by community. See post 'Timeline' for change history
  Retrieved 2026-03-23, License - CC BY-SA 3.0
  """

  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info")


setup(
  # ... Other setup options ...
  cmdclass={
    "clean": CleanCommand,
  },
)
