# SSH Connection Script
# This script connects to the remote server using SSH

$host = "45.82.72.136"
$user = "root"
$password = "*Adolfo1971*#2017$22"

Write-Host "Connecting to $user@$host..."
Write-Host "Note: You will be prompted to enter the password interactively."
Write-Host "Password: $password"
Write-Host ""

# Standard SSH connection (will prompt for password)
ssh "$user@$host"

