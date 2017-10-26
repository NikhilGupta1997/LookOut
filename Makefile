all: target

target:
	echo 'Target unknown'

clean:
	rm -rf *.pyc */*.pyc */*/*.pyc
