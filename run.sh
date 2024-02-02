#!/bin/bash

python3.8 setup.py build
python3.8 setup.py install

#python3.8 setup.py install --record files.txt
#cat files.txt | xargs rm -rf