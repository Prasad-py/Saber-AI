#!/bin/bash

if ! [[ -d $DIRNAME ]]
then
    export DIRNAME=""
fi

export VENV_PATH="$DIRNAME\saber-venv"

rm -rf $VENV_PATH
python -m venv $VENV_PATH
pip install -r "$DIRNAME\Saber-AI\requirements.txt"