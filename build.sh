#!/usr/bin/env bash
# cat /etc/os-release

sudo apt update

sudo apt install libpango1.0-0

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

#install npm dependencies
npm install

# Convert static asset files
python manage.py collectstatic --no-input


# Make users and data
# python generate.py shell
