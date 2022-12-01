#!/bin/bash

export RECREATE=false
export DIRNAME="D:\Saber"
export VENV_PATH="$DIRNAME\saber-venv"

if [[ $RECREATE == true ]]
then
    rm -rf $VENV_PATH
fi

if ! [[ -d $VENV_PATH ]]
then
    source "$DIRNAME\Saber-AI\create_venv.sh"
fi

source "$DIRNAME\saber-venv\Scripts\activate"

python "$DIRNAME\Saber\Saber-AI\run.py"