python3 -m venv venv
source venv/Scripts/activate
pip install -i https://download.pytorch.org/whl/cu121 torch torchvision
pip install -r requirements.txt
cd objects_counter || exit
flask db init
flask db upgrade
flask run
cd ..