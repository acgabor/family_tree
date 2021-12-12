#!/bin/bash
pyinstaller --onefile main.py -n family_tree.exe

: '
                            --exclude-module matplotlib \
'