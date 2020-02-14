#!/bin/bash
set -ex

./001a_analysis.sh
./001b_analysis.sh

./002_assemble.sh

./003_upload_staging.sh

./004a_upload_console_out.sh
./004b_upload_firings.sh

./005_generate_unit_details.sh
