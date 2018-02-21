import os
from subprocess import Popen, PIPE
import shlex
import datetime
import sys

# set constants
_MAX_ATTEMPTS = 10
_DELAY = .1
NOW = datetime.datetime.now()

QRI_COMMAND_TEMPLATE="""qri {action} \
--data "{DATA_PATH}" \
--structure "{STRUCTURE_PATH}" \
--meta "{META_PATH}" \
me/{DATASET_NAME}
"""

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

# get data
def fetch_data():
	#rename file if exists already
	if os.path.exists(DATA_PATH):
		cmd = "mv {path} prev_{path}".format(path=DATA_PATH)
		_shell_exec(cmd)
	#download file
	cmd = "wget -O {path} {url}".format(path=DATA_PATH, url=TARGET_URL)
	print("fetching data from '{}'...".format(TARGET_URL))
	result=_shell_exec(cmd)
	#print(result)
	print("download complete")


def _dataset_exists(DATASET_NAME):
	cmd = "qri info me/{} | grep ^error".format(DATASET_NAME)
	result = _shell_exec(cmd)
	if result == "":
		return True
	else:
		return False


def add_or_save_to_qri():
	action = "add"
	if _dataset_exists(DATASET_NAME):
		#add commit message and choose 'save'
		date_string = datetime.datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S")
		message = "recipe update @ {}".format(date_string)
		action = "save -m=\"{}\"".format(message)
	params = dict(
		action=action,
		DATA_PATH=DATA_PATH,
		STRUCTURE_PATH=STRUCTURE_PATH,
		META_PATH=META_PATH,
		DATASET_NAME=DATASET_NAME,
		)
	cmd = QRI_COMMAND_TEMPLATE.format(**params)
	result = _shell_exec(cmd)
	print(result)
	#print cmd

def main():
	if not TEST_RUN:
		fetch_data()
	add_or_save_to_qri()


if __name__ == "__main__":
	main()