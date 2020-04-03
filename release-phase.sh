#!/bin/bash

python3 manage.py migrate


python3 manage.py seed --reset_db=$RESET_DB
