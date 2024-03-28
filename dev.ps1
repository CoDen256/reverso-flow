Set-Variable -Name "FLOW_HOME" (Get-ChildItem -Dir -Path "~\scoop\apps\flow-launcher\current" -Filter 'app*').FullName
Remove-Item -Path "$FLOW_HOME\UserData\Plugins\Reverso-Flow-*" -Recurse -Force
New-Item -Path "$FLOW_HOME\UserData\Plugins\Reverso-Flow-Dev" -ItemType Junction -Value $PWD\..\reverso-flow -Force

python311.exe -m pip install -r "./requirements.txt" -t "./lib"

taskkill /f /im Flow*
Start-Process -FilePath "$FLOW_HOME\Flow.Launcher.exe"