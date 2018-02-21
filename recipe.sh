# NOTE remove the following line after docker is set up
source recipe_config.env

# if a data file exists rename it to avoid wget naming conflict
# if [ ! -f $r_data_file ]; then
#   mv $r_data_file prev_${r_data_file}
# fi

# # fetch the json file
# echo "fetching json file..."
# wget -o $r_data_file $r_target_url
# echo "data file retrieved"
# check to see if data exists in qri already
dataset_exists=false
# if attempting to get info for the dataset name prints a line 
# starting with 'error' then we keep 'dataset_exists', otherwise
# we set to true
if !("$(qri info me/${r_dataset_name} | grep ^error)"=""); then
	dataset_exists=true
fi

# yes this is redundant but just thought it helps make the bash 
# script more legible
action="add"
if dataset_exists; then
	#set a commit message
	message="recipe update @ $(date)"
	action="save -m=\"${}\""
fi

# save or add to qri
qri $action \
--data $r_data_file \
--structure $r_structure_file \
--meta $r_meta_file \
me/${r_dataset_name}