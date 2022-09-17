from __future__ import annotations
from grader.testing import TestCaseBase

from grader.testing.commands import Xv6ExecuteNone
from grader.testing.commands import Xv6ExecuteVariable
from grader.testing.commands import Xv6ExecuteFixed

from grader.exceptions import TestCaseExecErrors
from grader.exceptions import TestCaseIncorrect


def conv_ba_to_hashable(inarray: [bytearray]):
  for i in range(len(inarray)):
    inarray[i] = bytes(inarray[i])


class Case01(TestCaseBase):
  def __init__(self):
    super(Case01, self).__init__(
      "Test Case 01",
      "This is the first generic test case",
      30,
      hidden=True,
    )

    self.setup_ops = [
      Xv6ExecuteNone("mkdir TEST"),
      Xv6ExecuteNone("mkdir TEST2"),
      Xv6ExecuteNone("mkdir TEST3"),
      Xv6ExecuteNone("echo hellllo > TEST/sample.out"),
      Xv6ExecuteNone("echo helllo > TEST/sample2.out"),

    ]

    self.testing_ops = [
      Xv6ExecuteVariable("ls"),
      Xv6ExecuteNone("cd TEST"),
      Xv6ExecuteVariable("../ls")
    ]

    self.teardown_ops = []

  def evaluate(self):
    # throws

    # check cmd 1
    expected_list = [
      bytearray(b'.              1 1 512'),
      bytearray(b'..             1 1 512'),
      bytearray(b'README.md      2 2 3678'),
      bytearray(b'cat            2 3 19356'),
      bytearray(b'echo           2 4 18496'),
      bytearray(b'forktest       2 5 9192'),
      bytearray(b'grep           2 6 21368'),
      bytearray(b'init           2 7 19100'),
      bytearray(b'kill           2 8 18608'),
      bytearray(b'ln             2 9 18512'),
      bytearray(b'ls             2 10 20904'),
      bytearray(b'mkdir          2 11 18660'),
      bytearray(b'rm             2 12 18640'),
      bytearray(b'TEST           1 19 64'),
      bytearray(b'sh             2 13 30908'),
      bytearray(b'stressfs       2 14 19208'),
      bytearray(b'usertests      2 15 67896'),
      bytearray(b'wc             2 16 20084'),
      bytearray(b'zombie         2 17 18184'),
      bytearray(b'console        3 18 0'),
      bytearray(b'TEST2          1 20 32'),
      bytearray(b'TEST3          1 21 32'),
      bytearray(b'$ '),
    ]

    conv_ba_to_hashable(expected_list)

    actual_list = self.testing_ops[0].as_lines()

    conv_ba_to_hashable(actual_list)
    # check last line
    if expected_list[len(expected_list) - 1] != actual_list[len(actual_list) - 1]:
      raise TestCaseIncorrect

    # remove last lines, and check set validity
    expected_cmp = set(expected_list[:-1])
    actual_cmp = set(actual_list[:-1])
    if expected_cmp != actual_cmp:
      raise TestCaseIncorrect




