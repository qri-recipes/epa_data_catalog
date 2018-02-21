import os
from subprocess import Popen, PIPE
import shlex
import datetime
import time
import sys
import json
import requests
import re

_MAX_ATTEMPTS = 10
_DELAY = .1
NOW = datetime.datetime.now()
TIME_STAMP = datetime.datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S")

# --------------------------------------------------------------------
def _shell_exec_once(command):
    proc = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdoutdata, err = proc.communicate()
    if err != "":
        raise Exception(err)
    return stdoutdata

def _shell_exec(command):
    stdoutdata = _shell_exec_once(command)
    for _ in range(_MAX_ATTEMPTS - 1):
        if "error" not in stdoutdata[:15]:
            break
        time.sleep(_DELAY)
        stdoutdata = _shell_exec_once(command)
    return stdoutdata

# --------------------------------------------------------------------

# fetch_data retrieves a data.json file from the target url and saves
#   it to the data_path provided
def fetch_data(data_path, url):
  #rename file if exists already
  if os.path.exists(data_path):
    cmd = "mv {path} prev_{path}".format(path=data_path)
    _shell_exec(cmd)
  #download file
  print("fetching data from '{}'...".format(url))
  response = requests.get(url)
  data_string = response.text
  with open(data_path, "w") as fp:
    fp.write(data_string)
  print("download complete")

# update_meta_timestamp modifies the 'updated' field of the file at 
#   the meta_path with the string provided as timestamp
def update_meta_timestamp(meta_path, timestamp):
  with open(meta_path, "r") as fp:
    meta_dict = json.load(fp)
    meta_dict[u"updated"] = u"{}".format(timestamp)
  with open(meta_path, "w") as fp:
    fp.write(json.dumps(meta_dict, indent=2))

# _dataset_exists checks whether a dataset exists by attempting to 
#   request info on the dataset and seeing if it errors or not
def _dataset_exists(dataset_name):
  exists = True
  cmd = "qri info me/{}".format(dataset_name)
  result = _shell_exec_once(cmd)
  for line in result.split("\n"):
    if re.match(r'^error', line):
      exists = False
      break
  return exists

# --------------------------------------------------------------------

def add_qri_dataset(dataset_name, data_path, structure_path, meta_path):
  cmd = "qri add "
  cmd += "--data \"{}\" ".format(data_path)
  cmd += "--structure \"{}\" ".format(structure_path)
  cmd += "--meta \"{}\" ".format(meta_path)
  cmd += "me/{} ".format(dataset_name)
  # result = _shell_exec(cmd)
  result = _shell_exec_once(cmd)
  return result


def update_qri_dataset(dataset_name, data_path, structure_path, meta_path, commit_msg):
  cmd = "qri save "
  cmd += "-m \"{}\" ".format(commit_msg)
  cmd += "--data \"{}\" ".format(data_path)
  cmd += "--structure \"{}\" ".format(structure_path)
  cmd += "--meta \"{}\" ".format(meta_path)
  cmd += "me/{} ".format(dataset_name)
  # result = _shell_exec(cmd)
  result = _shell_exec_once(cmd)
  return result

def add_or_save_to_qri(dataset_name, data_path, structure_path, meta_path):
  if _dataset_exists(dataset_name):
    # set commit message and choose 'save'
    commit_msg = "recipe update @ {}".format(TIME_STAMP)
    result = update_qri_dataset(dataset_name, data_path, structure_path, meta_path, commit_msg)
  else:
    result = add_qri_dataset(dataset_name, data_path, structure_path, meta_path)
  return result


# --------------------------------------------------------------------
def main():
  # get variables from env
  try:  
     DATASET_NAME   = os.environ["r_dataset_name"]
     TARGET_URL     = os.environ["r_target_url"]
     DATA_PATH      = os.environ["r_data_path"]
     STRUCTURE_PATH = os.environ["r_structure_path"]
     META_PATH      = os.environ["r_meta_path"]
     TEST_RUN       = True if os.environ["r_test"] == "True" else False
  except KeyError as e: 
     print "Please ensure all required environment variales are set: missing {}".format(e)
  # prepare data.json
  if not TEST_RUN:
    fetch_data(DATA_PATH, TARGET_URL)
  if not os.path.exists(DATA_PATH):
    print("Unable to find '{}'".format(DATA_PATH))
  # prepare meta.json
  update_meta_timestamp(META_PATH, TIME_STAMP)
  # add or save dataset on qri
  output = add_or_save_to_qri(DATASET_NAME, DATA_PATH, STRUCTURE_PATH, META_PATH)
  # revert metadata.json to prevent udpates from being tracked in version control
  update_meta_timestamp(META_PATH,"")
  print(output)


  

if __name__ == "__main__":
  main()