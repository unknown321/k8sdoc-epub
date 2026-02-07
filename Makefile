MMDR_VERSION=0.1.3
MMDR_SHA256=577ac54b64a200003688a73d15f46ad9e09478412737d876652400d8997ae2e9

clean:
	rm -v *.html *.epub

veryclean: clean
	rm -rf img

mmdr:
	wget https://github.com/1jehuang/mermaid-rs-renderer/releases/download/v$(MMDR_VERSION)/mmdr-x86_64-unknown-linux-gnu.tar.gz
	echo -n "$(MMDR_SHA256) mmdr-x86_64-unknown-linux-gnu.tar.gz" | sha256sum -c -
	tar xf mmdr-x86_64-unknown-linux-gnu.tar.gz
	rm mmdr-x86_64-unknown-linux-gnu.tar.gz


prepare: mmdr
	pip install -r requirements.txt

run:
	python3 main.py

.PHONY: run clean veryclean
