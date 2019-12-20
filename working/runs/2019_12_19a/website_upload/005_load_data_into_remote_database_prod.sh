#!/bin/bash
set -e

./make_website_data.sh

cd ../website
./load_data_into_remote_database_prod.sh website_data