#!/bin/bash

export RECREATE=false
export DIRNAME=$1 # Path to the folder containing Saber-AI 
export VENV_PATH="$DIRNAME/saber-venv"
export REQUIREMENTS="$DIRNAME/Saber-AI/requirements.txt"

if [[ $RECREATE == true ]]
then
    rm -rf $VENV_PATH
fi

if ! [[ -d $VENV_PATH ]]
then
    source "$DIRNAME/Saber-AI/linux_create_venv.sh"
fi

source "$DIRNAME/saber-venv/Scripts/activate"

python3 "$DIRNAME/Saber-AI/run.py"