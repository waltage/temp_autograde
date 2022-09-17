from __future__ import annotations

import argparse
from argparse import Namespace
import os

from grader.testing.pipeline import PipelineConfig

ARGS = [
    ("--prod", dict(
        dest='prod', action='store_true',
        help='turn on production mode (for use in pipelines)')),
    ("--verbose", dict(
        dest='verbose', action='store_true',
        help='turn on verbose logging')),
    ("--netid", dict(
        dest='netid', default=None,
        help='netid of student (only needed in prod)')),
    ("--commit", dict(
        dest='commit', default=None,
        help='commit from repo to use (only needed in prod)')),
    ("--submission-id", dict(
        dest='submission_id', default=None,
        help='commit from repo to use (only needed in prod)')),
    ("--repo", dict(
        dest='repo', default=None,
        help='repo url to clone')),
    ("--path", dict(
        dest="path", default='.',
        help='path to student repo'))
]


def parse_autograder_args() -> Namespace:
  parser = argparse.ArgumentParser()
  for a in ARGS:
    parser.add_argument(a[0], **a[1])
  ns = parser.parse_args()
  inner_ns = vars(ns)

  if "TOKEN" in os.environ:
    inner_ns["token"] = os.environ.get("TOKEN")
    del os.environ["TOKEN"]
  else:
    inner_ns["token"] = None

  return ns
