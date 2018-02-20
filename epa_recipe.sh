wget https://edg.epa.gov/data.json
# Note: golang's standard library regexp does not support negative 
# look-aheads due to their time complexity. For now we will use a 
# schema that does not enforce patterns containing these and will
# update once the issue has been resolvedin jsonschema
structureFile="structure_noNegLookAheads.json"
#structureFile="structure.json"
qri add --data data.json --structure $structureFile me/epa_catalog