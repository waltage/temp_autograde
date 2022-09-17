from __future__ import annotations
from typing import List

from grader.adapters import MakeAdapterConfig
from grader.adapters import MakeAdapter
from grader.adapters import Xv6AdapterConfig
from grader.adapters import Xv6Adapter

from grader.testing.commands import Xv6Command

from grader.exceptions import BuildError
from grader.exceptions import BuildMakeError
from grader.exceptions import BuildCleanError

from grader.exceptions import Xv6AdapterError
from grader.exceptions import Xv6AdapterBootError
from grader.exceptions import Xv6AdapterIOError

from grader.exceptions import Xv6CommandError


class TestCaseBase:
  def __init__(self, name: str, desc: str, points: int, hidden: bool = False):
    self.name = name
    self.desc = desc
    self.points = points
    self.hidden = hidden
    self.otype = "unknown"
    self.setup_ops: List[Xv6Command] = []
    self.testing_ops: List[Xv6Command] = []
    self.teardown_ops: List[Xv6Command] = []

    self.start_clean = True
    self.stop_clean = True

    make_conf = MakeAdapterConfig(name)
    self.make_adapter = MakeAdapter(make_conf)

    xv6_conf = Xv6AdapterConfig(name)
    self.xv6_adapter = Xv6Adapter(xv6_conf)

  def add_setup(self, cmd: Xv6Command):
    self.setup_ops.append(cmd)

  def add_testing_ops(self, cmd: Xv6Command):
    self.testing_ops.append(cmd)

  def add_teardown_ops(self, cmd: Xv6Command):
    self.teardown_ops.append(cmd)
  
  def run_test(self):
    # throws exceptions
    if self.start_clean:
      self.make_adapter.clean()
      self.make_adapter.build()

    self.xv6_adapter.start_xv6()
    executed = True
    err = None
    try:
      for _ in self.setup_ops:
        _.execute(self.xv6_adapter)

      for _ in self.testing_ops:
        _.execute(self.xv6_adapter)

      for _ in self.teardown_ops:
        _.execute(self.xv6_adapter)

    except Xv6AdapterError as e:
      executed = False
      err = e
    except Xv6CommandError as e:
      executed = False
      err = e

    finally:
      self.xv6_adapter.stop_xv6()

      if self.stop_clean:
        self.make_adapter.clean()

      if not executed:
        raise err

  def evaluate(self):
    # throws
    raise NotImplementedError


