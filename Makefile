.PHONY: tests coverage covreport

tags:
	ctags -R .

tests:
	py.test -v tests/ -W "ignore"

coverage:
	pytest --cov=ig tests/ -W "ignore"

covreport:
	pytest --cov=ig tests/ -W "ignore" && coverage html

onetest:
	py.test -s tests/test_$(tname).py -W "ignore"
