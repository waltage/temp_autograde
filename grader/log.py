import logging

LOG_FORMAT = "[%(levelname)-8s] %(asctime)s::%(name)30s:: %(message)s"


def log_init(level: int = logging.DEBUG):
  logging.basicConfig(level=level,
                      format=LOG_FORMAT,
                      )
