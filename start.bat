python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -i https://download.pytorch.org/whl/cu121 -r requirements-torch.txt
IF NOT "%~1"=="" SET "SAM_CHECKPOINT=%~1"
IF "%SAM_CHECKPOINT%"=="" (
    ECHO "SAM_CHECKPOINT not specified"
    EXIT /B 1
)
cd objects_counter
flask db init
flask db upgrade
flask run
cd ..