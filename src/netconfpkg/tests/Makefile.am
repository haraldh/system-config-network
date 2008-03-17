TESTS_ENVIRONMENT = PYTHONPATH=${srcdir}/../:@PY_PYTHONPATH@
TESTS = test-Conf.py test-rcn.py test-hosts.py
EXTRA_DIST = $(TESTS) test-root coverage.py test-gui.py hosts hosts2

CLEANFILES := .coverage stdout stderr $(notdir $(wildcard *,cover)) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard *.pyc))

pylint: $(PYTHON_FILES)
	@echo "Running pylint"
	@! pylint --errors-only --rcfile=$(top_srcdir)/pylintrc $(subst .py,,$(TESTS)) 2>/dev/null | egrep '^E:'
	