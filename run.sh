# TODO: remove the following line after docker is set up
# TODO: remove 'export' from recipe_config.env
source recipe_config.env

# install python dependencies
pip install -r requirements.txt

#execute
python recipe.py