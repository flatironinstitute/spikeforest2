#!/bin/bash

set -e

../../../../spike-front/admin/bin/delete-data.js --database-from-env-prod --delete
../../../../spike-front/admin/bin/format-and-load-data.js $1 --database-from-env-prod
