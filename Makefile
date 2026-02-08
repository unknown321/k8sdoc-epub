KEPUBIFY_VERSION=v4.0.4
KEPUBIFY_SHA256=37d7628d26c5c906f607f24b36f781f306075e7073a6fe7820a751bb60431fc5

kepubify:
	wget https://github.com/pgaskin/kepubify/releases/download/$(KEPUBIFY_VERSION)/kepubify-linux-64bit
	echo -n "$(KEPUBIFY_SHA256) kepubify-linux-64bit" | sha256sum -c -
	chmod +x kepubify-linux-64bit

clean:
	-rm -v *.html *.epub

veryclean: clean
	rm -rf img

prepare: kepubify
	pip install -r requirements.txt

run:
	python3 main.py
	./kepubify-linux-64bit --no-add-dummy-titlepage -i *.epub

.PHONY: run clean veryclean
