#!/bin/bash

if ! [[ -d $DIRNAME ]]
then
    export DIRNAME=$1 # Path to the folder containing Saber-AI 
    
fi

if ! [[ -f $REQUIREMENTS ]]
then
    export REQUIREMENTS="$DIRNAME/Saber-AI/requirements.txt" # Path to requirements.txt
fi

export VENV_PATH="$DIRNAME/saber-venv"
echo "Creating Virtual Environment at $VENV_PATH"

rm -rf $VENV_PATH

python3 -m venv $VENV_PATH
source "$DIRNAME/saber-venv/Scripts/activate"
python3 -m pip install --upgrade pip
pip3 install -r "$DIRNAME/Saber-AI/requirements.txt"

pip3 freeze