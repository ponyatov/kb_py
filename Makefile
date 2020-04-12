CWD    = $(CURDIR)
MODULE = $(notdir $(CWD))

NOW = $(shell date +%d%m%y)
REL = $(shell git rev-parse --short=4 HEAD)

PIP = $(CWD)/bin/pip3
PY  = $(CWD)/bin/python3
PYT = $(CWD)/bin/pytest

.PHONY: all py rust
all:

py: $(MODULE).py $(MODULE).ini
	$(PYT) --quiet $< && $(PY) $^
rust: target/debug/$(MODULE) $(MODULE).ini
	$^

target/debug/$(MODULE): $(MODULE).rs Cargo.toml Makefile
	cargo build && size $@


.PHONY: install
install: os $(PIP)
	$(PIP) install    -r requirements.txt
	$(MAKE) requirements.txt

.PHONY: update
update: os $(PIP)
	$(PIP) install -U -r requirements.txt
	$(MAKE) requirements.txt

$(PIP) $(PY):
	python3 -m venv .
	$(CWD)/bin/pip3 install -U pip pytest pylint autopep8

.PHONY: requirements.txt
requirements.txt: $(PIP)
	$< freeze | grep -v 0.0.0 > $@

.PHONY: os
ifeq ($(OS),Windows_NT)
os: windows
else
os: debian
endif

.PHONY: debian
debian:
	sudo apt update
	sudo apt install -u \
		python3 python3-venv


.PHONY: master shadow release zip

MERGE  = Makefile README.md .gitignore .vscode
MERGE += requirements.txt $(MODULE).* static templates
MERGE += *rs Cargo.toml

master:
	git checkout $@
	git checkout shadow -- $(MERGE)

shadow:
	git checkout $@

release:
	git tag $(NOW)-$(REL)
	git push -v && git push -v --tags
	git checkout shadow

zip:
	git archive --format zip --output $(MODULE)_src_$(NOW)_$(REL).zip HEAD
