python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -i https://download.pytorch.org/whl/cu121 -r requirements-torch.txt
cd objects_counter
flask db init
flask db upgrade
flask run
cd ..