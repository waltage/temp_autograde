from __future__ import annotations

import logging
import os
from typing import List

import yaml

from grader.exceptions import AutoGradeError
from grader.exceptions import PipelineMetadataError
from grader.exceptions import TestCaseIncorrect
from grader.testing import TestCaseBase


class PipelineConfig:
  def __init__(self):
    self.verbose = False
    self.prod = False
    self.netid = ""
    self.commit = ""
    self.submission_id = ""
    self.repo = ""
    self.path = "../grader"
    self.token = None
    self.xv6_buffer = 1024


class Pipeline:
  def __init__(self, pipeline_conf: PipelineConfig):
    self.pipeline_conf = pipeline_conf
    self.logger = logging.getLogger("Pipeline")
    self.tests: List[TestCaseBase | None] = []

  def add_test(self, test_case: TestCaseBase):
    self.tests.append(test_case)

  def load_metadata(self) -> dict:
    filename = None
    for f in ("meta.yml", "meta.yaml"):
      if os.path.isfile(f):
        filename = f
        break
    if not filename:
      raise PipelineMetadataError("cannot find metadata")

    with open(filename, "r") as f:
      try:
        metadata = yaml.safe_load(f.read())
      except yaml.YAMLError as e:
        raise PipelineMetadataError("cannot parse metadata", e)

    self.logger.debug("assignment_metadata: {}", metadata)
    return metadata

  def run_tests(self) -> [AutoGradeError | None]:
    # throws
    errors = []
    for test_case in self.tests:
      executed = True
      try:
        test_case.run_test()
      except AutoGradeError as e:
        errors.append(e)
        executed = False

      if not executed:
        continue

      correct = True
      try:
        test_case.evaluate()
      except TestCaseIncorrect as e:
        errors.append(e)
        correct = False
      except AutoGradeError as e:
        errors.append(e)
        correct = False

      if correct:
        errors.append(None)

    return errors

