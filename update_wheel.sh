#! /bin/bash

cd ~/repos/github/eneboo-tools
rm dist/*
rm -Rf build/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/* 
sudo -H pip3 install --upgrade enebootools --break-system-packages
sudo -H pip3 install --upgrade enebootools --break-system-packages
