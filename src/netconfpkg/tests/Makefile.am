TESTS_ENVIRONMENT = PYTHONPATH=${srcdir}/../:@PY_PYTHONPATH@
TESTS = test-Conf.py test-rcn.py test-hosts.py
EXTRA_DIST = $(TESTS) test-root coverage.py test-gui.py hosts hosts2

CLEANFILES := .coverage stdout stderr $(notdir $(wildcard *,cover)) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard *.pyc))

pylint: $(PYTHON_FILES)
	@echo "Running pylint"
	@! pylint --errors-only --rcfile=$(top_srcdir)/pylintrc $(subst .py,,$(TESTS)) 2>/dev/null | egrep '^E:'

check-local:
	@for i in $(GLADE_FILES)  $(PYTHON_FILES); do test -f $(srcdir)/$$i || (echo $$i is missing;break);done && echo "Source file check PASSED"
	@for i in $(notdir $(wildcard *.py)); do echo $(TESTS) $(EXTRA_DIST)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
	
