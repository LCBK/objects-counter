python3 -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
pip install -i https://download.pytorch.org/whl/cu121 -r requirements-torch.txt
cd objects_counter || exit
flask db init
flask db upgrade
flask run
cd ..