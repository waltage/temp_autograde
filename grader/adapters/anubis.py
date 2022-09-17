import logging
import requests


class AnubisAdapterConfig:
  def __init__(self, logger_name: str = "default"):
    self.logger = logging.getLogger("AnubisAdapter.{}".format(logger_name))
    self.token: str = ""
    self.commit: str = ""
    self.submission_id: str = ""


class AnubisAdapter:
  def __init__(self, conf: AnubisAdapterConfig):
    self.conf = conf

  def report_state(self, state: str, params=None):
    body = dict(
      token=self.conf.token,
      commit=self.conf.commit,
      state=state)
    self.conf.logger.debug("report_state: {}".format(body))
    self.__send(
      "/pipeline/report/state/{}".format(self.conf.submission_id),
      body,
      params=params
    )

  def report_build_result(self, message: str, status: bool):
    body = dict(
      token=self.conf.token,
      commit=self.conf.commit,
      stdout=message,
      passed=status)
    self.conf.logger.debug("report_build: {}".format(body))
    self.__send(
      "/pipeline/report/build/{}".format(self.conf.submission_id),
      body)

  def report_test_result(self, name: str, otype: str, message: str, status: bool):
    body = dict(
      token=self.conf.token,
      commit=self.conf.commit,
      test_name=name,
      output_type=otype,
      message=message,
      passed=status
    )
    self.conf.logger.debug("report_test_results: {}".format(body))
    self.__send(
      "/pipeline/report/test/{}".format(self.conf.submission_id),
      body)

  def panic(self, msg: str, trace: str = None):
    """Panic sends a panic to anubis and EXITS program."""
    body = dict(
      token=self.conf.token,
      commit=self.conf.commit,
      message=msg,
      traceback=trace,
    )
    self.conf.logger.error("anubis: sending panic: {}".format(body))
    self.__send(
      "/pipeline/report/panic/{}".format(self.conf.submission_id),
      body
    )
    exit(2)

  def __send(self, path: str, data: dict, params=None):
    if not params:
      params = {}
    headers = {"Content-type": "application/json"}
    params["token"] = self.conf.token
    try:
      response = requests.post(
        "http://anubis-pipeline-api:5000{}".format(path),
        headers=headers,
        params=params,
        json=data
      )
      if response.status_code != 200:
        self.conf.logger.error("UNABLE TO REPORT POST TO PIPELINE API")
        exit(1)

      return response
    except Exception as e:
      self.conf.logger.error("UNABLE TO REPORT POST TO PIPELINE API")
      exit(1)
