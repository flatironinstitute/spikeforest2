#!/bin/bash
set -e

./make_website_data_directory.py $1 -o website_data
./load_data_into_remote_database.sh website_data