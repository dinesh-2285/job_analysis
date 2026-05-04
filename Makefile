install:
\tpython -m pip install -r requirements.txt

backend:
\tuvicorn backend.app.main:app --reload

frontend:
\tstreamlit run frontend/app.py

test:
\tpytest

lint:
\tpython -m compileall backend frontend ml
