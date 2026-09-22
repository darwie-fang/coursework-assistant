#!/bin/zsh
cd -- "${0:A:h}/.."
if command -v python3 >/dev/null 2>&1; then
  python3 work/courseworks.py setup
else
  print 'Python 3 is required. Install it from python.org, then try again.'
fi
read '?Press Return to close this window.'
