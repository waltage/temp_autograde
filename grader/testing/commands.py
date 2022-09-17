from __future__ import annotations

import re

from grader.adapters.xv6 import Xv6Adapter
from grader.exceptions import Xv6CommandReadBackError
from grader.exceptions import Xv6CommandResponseError


class Xv6Command:
  def __init__(self, send: bytes, recv_size: int = -1):
    self.send_bytes: bytearray = bytearray(send)
    self.exp_resp_size = recv_size
    self.response = dict(
      size=0,
      bytes=bytearray(),
      err=bytearray()
    )

  def _send_command(self, adapter: Xv6Adapter):
    if self.send_bytes[-1:] != b'\n':
      self.send_bytes.extend(b'\n')
    adapter.send_stdin(self.send_bytes)
    result = adapter.read_stdout(len(self.send_bytes))
    if result != self.send_bytes:
      raise Xv6CommandReadBackError("received: {}".format(repr(result)))

  def _fill_response(self, adapter: Xv6Adapter):
    if self.exp_resp_size == -1:
      # expect no output... verify shell prompt is present
      ahead = adapter.peek_stdout(2)
      if ahead != b'$ ':
        self.response["err"] = adapter.read_stdout(0)
        adapter.stop_xv6()
        raise Xv6CommandResponseError(
          "shell prompt expected",
          "received {}".format(repr(self.response["err"])))
      else:
        # got a shell prompt... skip it
        adapter.seek_stdout(2)

    if self.exp_resp_size > -1:
      self.response["bytes"] = adapter.read_stdout(self.exp_resp_size)
      self.response["size"] = len(self.response["bytes"])

  def _check_response(self):
    panics = re.search(b"(panic|trap)", self.response["bytes"])
    if panics:
      raise Xv6CommandResponseError("unrecoverable error",
                                    "got panic/trap: {}".format(panics.groups()))

  def execute(self, adapter: Xv6Adapter):
    self._send_command(adapter)
    # this throws....
    self._fill_response(adapter)
    # this throws....
    self._check_response()

  def as_lines(self):
    if self.response["size"] == 0:
      return []
    else:
      return self.response["bytes"].splitlines(False)


class Xv6ExecuteNone(Xv6Command):
  """Execute a command with no expected response."""
  def __init__(self, cmd: str):
    super(Xv6ExecuteNone, self).__init__(
      bytearray(cmd, "utf-8"),
      -1
    )


class Xv6ExecuteFixed(Xv6Command):
  """Execute a command with a fixed-sized expected response."""
  def __init__(self, cmd: str, n: int):
    super(Xv6ExecuteFixed, self).__init__(
      bytearray(cmd, "utf-8"),
      n
    )


class Xv6ExecuteVariable(Xv6Command):
  """Execute a command with a variable-sized expected resuponse"""
  def __init__(self, cmd: str):
    super(Xv6ExecuteVariable, self).__init__(
      bytearray(cmd, "utf-8"),
      0
    )
