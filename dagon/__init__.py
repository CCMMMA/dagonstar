import json
import logging
import logging.config
from logging.config import fileConfig
from graphviz import Digraph 
from enum import Enum

class Status(Enum):
  READY = "READY"
  WAITING= "WAITING"
  RUNNING = "RUNNING"
  FINISHED = "FINISHED"
  FAILED = "FAILED"

class Workflow(object):

  SCHEMA="workflow://"

  def __init__(self,name,cfg):
    fileConfig('dagon.ini')
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("globus_sdk").setLevel(logging.WARNING)
    self.logger = logging.getLogger()

    self.name=name
    self.cfg=cfg
    self.tasks=[]

  def get_scratch_dir_base(self):
    return self.cfg['scratch_dir_base']

  def find_task_by_name(self,name):
    for task in self.tasks:
      if name in task.name:
        return task
    return None

  def add_task(self,task):
    self.tasks.append(task)
    task.set_workflow(self)

  def make_dependencies(self):
    # Clean all dependencies
    for task in self.tasks:
      task.nexts=[]
      task.prevs=[]
      task.reference_count=0

    # Automatically detect dependencies
    for task in self.tasks:
      # Invoke pre run
      task.pre_run()

  # Return a json representation of the workflow
  def asJson(self):
    jsonWorkflow={ "tasks":[] }
    for task in self.tasks:
      jsonWorkflow['tasks'].append(task.asJson())
    return jsonWorkflow

  def run(self):
    self.logger.debug("Running workflow: %s",self.name)
    for task in self.tasks:
      task.start()

  def draw(self):
    g = Digraph(self.name)
    g.node_attr.update(color='lightblue2', style='filled')
    #g.edge("x","z")
    #g.edge("x", "y")
    #g.view()
    for task in self.tasks:
      g.node(task.name, task.name)
      for child in task.nexts:
        g.edge(task.name, child.name)
      #g.edge(task.name,)
    g.view()

def readConfig(section):
  import configparser
  config = configparser.ConfigParser()
  config.read('dagon.ini')
  return dict(config.items(section))