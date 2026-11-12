PYTHON ?= python
.PHONY: dev serve test check eval build browser smoke
dev serve test check eval build browser smoke:
	$(PYTHON) manage.py $@
