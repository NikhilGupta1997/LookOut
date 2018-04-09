all: target

target:
	python test.py

clean:
	rm -rf *.pyc */*.pyc */*/*.pyc
