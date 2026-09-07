#!/usr/bin/env sh

#mix run --no-halt

# ENTER SU mode for GPIO access under anything other than Raspberry OS

#. activate
#source activate_py3_venv
source uv-venv/bin/activate
doas iex -S mix
