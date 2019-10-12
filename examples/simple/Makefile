.PHONY: clean build install uninstall

clean:
	npm clean

install-ts:
	npm install
	
build-ts:
	npm run build

build:
	pip install -e .

install:
	python setup.py install

uninstall:
	pip uninstall -y simple_ext

start1+2:
	jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}"

start1:
	jupyter simple-ext1

start2:
	jupyter simple-ext2
