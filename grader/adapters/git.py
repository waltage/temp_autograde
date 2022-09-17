import git
import logging
import os

from grader.adapters.anubis import AnubisAdapter


class GitAdapterConfig:
  def __init__(self):
    self.repo = ""
    self.path = ""
    self.commit = ""
    self.prod = False
    self.logger = logging.getLogger("GitAdapter")


class GitAdapter:
  def __init__(self, conf: GitAdapterConfig):
    self.conf = conf

  def clone_student_repo(self):
    self.conf.logger.debug("git: setting credentials")
    git_creds = os.environ.get('GIT_CRED', default=None)
    if git_creds is not None:
      del os.environ['GIT_CRED']
      with open(os.environ.get('HOME') + '/.git-credentials', 'w') as f:
        f.write(git_creds)
        f.close()
      with open(os.environ.get('HOME') + '/.gitconfig', 'w') as f:
        f.write('[core]\n')
        f.write('\thooksPath = /dev/null\n')
        f.write('[credential]\n')
        f.write('\thelper = store\n')
        f.close()
    else:
      with open(os.environ.get('HOME') + '/.gitconfig', 'w') as f:
        f.write('[core]\n')
        f.write('\thooksPath = /dev/null\n')
        f.close()

    self.conf.logger.debug("git: clone student repo")
    try:
      repo = git.Repo.clone_from(self.conf.repo, self.conf.path)
      if self.conf.commit and self.conf.commit.lower() not in ("", "null"):
        self.conf.logger.debug("git: checking out commit '%s'", self.conf.commit)
        repo.git.checkout(self.conf.commit)
    except git.exc.GitCommandError as gce:
      self.conf.logger.error("git: could not clone and/or checkout err='%s'", gce)
      raise gce

    if self.conf.prod:
      self.conf.logger.debug("git: cleaning up local environment")
      os.system("rm -rf {}/.git".format(self.conf.path))
      os.system("rm -rf /home/anubis/.git-credentials")
      os.system("rm -rf /home/anubis/.gitconfig")
      os.system("chmod 777 -R {}".format(self.conf.path))
