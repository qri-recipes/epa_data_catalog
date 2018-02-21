import os
import subprocess
import datetime
import sys

# set constants
_MAX_ATTEMPTS = 10
_DELAY = .1
NOW = datetime.datetime.now()

QRI_COMMAND_TEMPLATE="""qri {action} \
--data "{data_path}" \
--structure "{structure_path} \
--meta "{meta_path} \
me/{dataset_name}
"""

# get variables from env
try:  
   dataset_name   = os.environ["r_dataset_name"]
   target_url     = os.environ["r_target_url"]
   data_path      = os.environ["r_data_path"]
   structure_path = os.environ["r_structure_path"]
   meta_path      = os.environ["r_meta_path"]
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


def _dataset_exists(dataset_name):
	cmd = "qri info me/{} | grep ^error".format(dataset_name)
	result = _shell_exec(cmd)
	if result == "":
		return True
	else:
		return False

action = "add"
if _dataset_exists(dataset_name):
	#add commit message and choose 'save'
	date_string = datetime.datetime.strftime(NOW, "%Y-%m-%dT%H:%M:%S")
	message = "recipe update @ {}".format(date_string)
	action = "save -m=\"{}\"".format(message)

# get data
# if a data file exists rename it to avoid wget naming conflict
# if [ ! -f $r_data_file ]; then
#   mv $r_data_file prev_${r_data_file}
# fi

# # fetch the json file
# echo "fetching json file..."
# wget -o $r_data_file $r_target_url
# echo "data file retrieved"
