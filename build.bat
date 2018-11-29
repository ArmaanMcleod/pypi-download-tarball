@echo off

if not "%~1" == "" (goto :%1 2>nul)
goto :default

:install
pip install -r requirements.txt
goto:eof

:clean
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q download_tarball.egg-info
goto:eof

:setup
python setup.py sdist
python setup.py bdist_wheel
goto:eof

:test
python tests.py
goto:eof

:upload
twine upload dist/*
goto:eof

:default
echo USAGE: build.bat (rule)
echo Build Script rules:
echo install - Install dependencies.
echo clean - Clean generated directories.
echo setup - Setup source distribution and wheel.
echo upload - Upload source distribution and wheel to PyPi.
echo test - Run sample tests.