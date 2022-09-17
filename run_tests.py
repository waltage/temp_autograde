#!/usr/bin/python3
import argparse
import logging
import os

import git.exc

from grader.adapters.anubis import AnubisAdapter
from grader.adapters.anubis import AnubisAdapterConfig
from grader.adapters.git import GitAdapter
from grader.adapters.git import GitAdapterConfig
from grader.args import parse_autograder_args
from grader.cases import Case01
from grader.log import log_init
from grader.testing.pipeline import Pipeline
from grader.testing.pipeline import PipelineConfig

ARGS = parse_autograder_args()


def configure_anubis(args: argparse.Namespace) -> AnubisAdapter:
  anubis_conf = AnubisAdapterConfig()
  anubis_conf.submission_id = args.submission_id
  anubis_conf.commit = args.commit
  anubis_conf.token = args.token
  return AnubisAdapter(anubis_conf)


def configure_git(args: argparse.Namespace) -> GitAdapter:
  git_conf = GitAdapterConfig()
  git_conf.repo = args.repo
  git_conf.path = args.path
  git_conf.commit = args.commit
  git_conf.prod = args.prod
  return GitAdapter(git_conf)


def configure_pipeline(args: argparse.Namespace) -> Pipeline:
  conf = PipelineConfig()
  conf.verbose = args.verbose
  conf.prod = args.prod
  conf.netid = args.netid
  conf.commit = args.commit
  conf.submission_id = args.submission_id
  conf.repo = args.repo
  conf.path = args.path
  conf.token = args.token
  return Pipeline(conf)


def main():
  if ARGS.verbose:
    log_init()
  else:
    log_init(logging.WARNING)

  anubis_adapter = configure_anubis(ARGS)
  git_adapter = configure_git(ARGS)

  # init git... send status
  try:
    git_adapter.clone_student_repo()
  except git.exc.GitCommandError as ge:
    # this automatically exits
    anubis_adapter.panic("could not clone and/or checkout repository", )

  os.chdir(ARGS.path)

  # init pipeline, fill and run
  pipeline = configure_pipeline(ARGS)

  pipeline.add_test(Case01())
  pipeline.add_test(Case01())
  pipeline.add_test(Case01())


  results = pipeline.run_tests()

  # send status
  print(results)


if __name__ == "__main__":
  main()
