python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -i https://download.pytorch.org/whl/cu121 -r requirements-torch.txt
IF NOT "%~1"=="" SET "SAM_CHECKPOINT=%~1"
IF "%SAM_CHECKPOINT%"=="" (
    ECHO "SAM_CHECKPOINT not specified"
    EXIT /B 1
)
IF NOT "%~2"=="" SET "SAM_MODEL_TYPE=%~2"
cd objects_counter
flask db upgrade
flask run --host=0.0.0.0
cd ..