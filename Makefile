.PHONY:

.venv/touchfile: requirements.txt
 	ifeq (, $(shell which virtualenv))
 		$(error "Could not find virtualenv, consider doing `pip install virtualenv`")
 	endif	
	test -d .venv || virtualenv .venv
	. .venv/bin/activate ; pip install -Ur requirements.txt
	touch .venv/touchfile

freeze: .venv/touchfile
	set -e ; . .venv/bin/activate ; pip freeze
	
run: .venv/touchfile
	set -e ; . .venv/bin/activate ; python3 icompose

clean:
	rm -rf .venv build dist *.egg-info .pytest-cache
	find -iname "*.pyc" -delete
	find -iname "__pycache__" -delete

