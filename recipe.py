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
--data "{data_path}" \
--structure "{structure_path}" \
--meta "{meta_path}" \
me/{dataset_name}
"""

# get variables from env
try:  
   dataset_name   = os.environ["r_dataset_name"]
   target_url     = os.environ["r_target_url"]
   data_path      = os.environ["r_data_path"]
   structure_path = os.environ["r_structure_path"]
   meta_path      = os.environ["r_meta_path"]
   test_run       = True if os.environ["r_test"] == "True" else False
except KeyError: 
   print "Please ensure all required environment variales are set"
   sys.exit(1)

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
	if os.path.exists(data_path):
		cmd = "mv {path} prev_{path}".format(path=data_path)
		_shell_exec(cmd)
	#download file
	cmd = "wget -O {path} {url}".format(path=data_path, url=target_url)
	print("fetching data from '{}'...".format(target_url))
	result=_shell_exec(cmd)
	#print(result)
	print("download complete")


def _dataset_exists(dataset_name):
	cmd = "qri info me/{} | grep ^error".format(dataset_name)
	result = _shell_exec(cmd)
	if result == "":
		return True
	else:
		return False


def add_or_save_to_qri():
	action = "add"
	if _dataset_exists(dataset_name):
		#add commit message and choose 'save'
		date_string = datetime.datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S")
		message = "recipe update @ {}".format(date_string)
		action = "save -m=\"{}\"".format(message)
	params = dict(
		action=action,
		data_path=data_path,
		structure_path=structure_path,
		meta_path=meta_path,
		dataset_name=dataset_name,
		)
	cmd = QRI_COMMAND_TEMPLATE.format(**params)
	result = _shell_exec(cmd)
	print(result)
	#print cmd

def main():
	if not test_run:
		fetch_data()
	add_or_save_to_qri()


if __name__ == "__main__":
	main()

# get data
# if a data file exists rename it to avoid wget naming conflict
# if [ ! -f $r_data_file ]; then
#   mv $r_data_file prev_${r_data_file}
# fi

# # fetch the json file
# echo "fetching json file..."
# wget -o $r_data_file $r_target_url
# echo "data file retrieved"
