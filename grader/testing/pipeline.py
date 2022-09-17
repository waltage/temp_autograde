from __future__ import annotations

import logging
import os
from typing import List

import yaml

from grader.adapters import AnubisAdapter
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
    self.anubis_adapter: AnubisAdapter | None = None


class Pipeline:
  def __init__(self, pipeline_conf: PipelineConfig):
    self.pipeline_conf: PipelineConfig = pipeline_conf
    self.logger = logging.getLogger("Pipeline")
    self.tests: List[TestCaseBase | None] = []
    self.first_build_alert = False

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

  def send_build_confirmation(self):
    if not self.first_build_alert:
      self.pipeline_conf.anubis_adapter.report_build_result("at least one test built correctly", True)
      self.first_build_alert = True

  def run_tests(self) -> [AutoGradeError | None]:
    # throws
    errors = []
    for test_case in self.tests:
      executed = True
      # try to run it...
      try:
        test_case.run_test()
      except AutoGradeError as e:
        errors.append(e)
        executed = False

      if not executed:
        continue

      # update build if it's not done yet
      if not self.first_build_alert:
        self.pipeline_conf.anubis_adapter.report_build_result("at least one test built correctly", True)
        self.first_build_alert = True

      # try to verify it as correct
      correct = True
      try:
        test_case.evaluate()
      except TestCaseIncorrect as e:
        errors.append(e)
        self.pipeline_conf.anubis_adapter.report_test_result(
          test_case.name, test_case.otype, test_case.desc, False)
        correct = False
      except AutoGradeError as e:
        self.pipeline_conf.anubis_adapter.report_state("auto grade encountered error")
        errors.append(e)
        correct = False

      if correct:
        errors.append(None)
        self.pipeline_conf.anubis_adapter.report_test_result(
          test_case.name, test_case.otype, test_case.desc, True)

    if not self.first_build_alert:
      self.pipeline_conf.anubis_adapter.report_build_result("could not build any tests", False)

    return errors

