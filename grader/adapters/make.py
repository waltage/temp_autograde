import logging
import subprocess

from grader.exceptions import BuildMakeError
from grader.exceptions import BuildCleanError


class MakeAdapterConfig:
  def __init__(self, log_name: str = "default"):
    self.logger = logging.getLogger("MakeAdapter.{}".format(log_name))


class MakeAdapter:
  def __init__(self, build_conf: MakeAdapterConfig):
    self.conf = build_conf

  def build(self):
    self.conf.logger.debug("make: building")
    make_session = subprocess.Popen(
      ["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    make_session.wait(4)
    if make_session.returncode != 0:
      self.conf.logger.error("make: build -- non-zero exit code")
      raise BuildMakeError("non-zero exit code")
    self.conf.logger.debug("make: build complete.")

  def clean(self):
    self.conf.logger.debug("make: cleaning")
    make_session = subprocess.Popen(
      ["make", "clean"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    make_session.wait(3)
    if make_session.returncode != 0:
      self.conf.logger.error("make: clean -- non-zero exit code")
      raise BuildCleanError("non-zero exit code")
    self.conf.logger.debug("make: clean complete.")


