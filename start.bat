python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

cd objects_counter
flask db init
flask db upgrade
flask run
cd ..