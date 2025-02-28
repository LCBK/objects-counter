#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -i https://download.pytorch.org/whl/cu121 -r requirements-torch.txt
if [ -z "$1" ]
then
    echo "Getting the checkpoint from environment variable"
else
    export SAM_CHECKPOINT=$1
fi
if [ -z $SAM_CHECKPOINT ]
then
    echo "SAM_CHECKPOINT is not set"
    exit 1
else
    echo "SAM_CHECKPOINT is set to $SAM_CHECKPOINT"
fi
if [ -n "$2" ]
then
    export SAM_MODEL_TYPE=$2
fi
cd objects_counter || exit
echo "Enter the database password: "
read -s -r db_password
export DB_PASSWORD=$db_password
flask db upgrade
flask run --host=0.0.0.0
cd ..
