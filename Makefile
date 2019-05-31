SHELL=/bin/bash

.PHONY: dist/borg_qt

dist/borg-qt: venv
	( \
	. venv/bin/activate; \
	pyinstaller --hidden-import=PyQt5.sip \
		--add-data=borg_qt/static/icons:borg_qt/static/icons \
		--add-data=borg_qt/static/UI:borg_qt/static/UI -n borg_qt\
		-F borg_qt/__main__.py; \
	)

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip3 install wheel; pip3 install -Ur requirements.txt
	touch venv/bin/activate

init:
	rm -rf venv
	python3 -m venv venv
	. venv/bin/activate
	( \
	pip3 install -r requirements.txt; \
	pip3 install -e .; \
	TEST_REPO=/tmp/test-borgqt; \
	export BORG_REPO=$$TEST_REPO; \
	export BORG_PASSPHRASE='foo'; \
	rm -rf $$TEST_REPO; \
	mkdir $$TEST_REPO; \
	borg init -e repokey-blake2; \
	)

test:
	@. venv/bin/activate
	@( \
	cd tests/; \
	pytest; \
	)

clean: distclean
	rm -rf build/
	rm -rf venv/
	find -iname "*.pyc" -delete

distclean:
	rm -rf dist/
