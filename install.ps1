# Stop execution if there is an error
$ErrorActionPreference = "Stop"

Write-Host "Installing Library Management Web Application`n`n"

Write-Host "Creating .env file.`n`n"
Copy-Item -Path "example.env" -Destination ".env"

Write-Host "Installing dependencies.`n"
poetry install

Write-Host "Setting up SECRET_KEY.`n`n"
$SECRET_KEY = python3 -c 'import secrets; print(secrets.token_hex(32))'
Add-Content -Path ".env" -Value "`nSECRET_KEY=$SECRET_KEY"

Write-Host "Setting up Flask Application and Database.`n`n"
poetry run flask db upgrade

Write-Host "Installation completed.`n`n"
Write-Host "Run 'poetry run flask run' to run the Web Application."
