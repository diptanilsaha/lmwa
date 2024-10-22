#!/bin/bash
set -e

echo -e "Installing Library Management Web Application\n\n"

echo -e "Creating .env file.\n\n"
cp example.env .env

echo -e "Installing dependencies.\n"
poetry install

echo -e "Setting up SECRET_KEY.\n\n"
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo -e "\nSECRET_KEY=$SECRET_KEY" >> .env

echo -e "Setting up Flask Application and Database.\n\n"
poetry run flask db upgrade

echo -e "Installation completed.\n\n"
echo -e "Run 'poetry run flask run' to run the Web Application."