python -m venv venv
call venv\Scripts\activate.bat
pip install -i https://download.pytorch.org/whl/cu121 torch torchvision
pip install -r requirements.txt

cd objects_counter
flask db init
flask db upgrade
flask run
cd ..