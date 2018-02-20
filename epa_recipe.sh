# NOTE remove the following line after docker is set up
source recipe_config.env

# fetch the json file
wget -o $r_data_file $r_target_url

# add to qri
qri add \
--data $r_data_file \
--structure $r_structure_file \
me/${r_dataset_name}