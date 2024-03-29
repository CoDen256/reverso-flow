taskkill /f /im Flow*

Set-Variable -Name "FLOW_HOME" (Get-ChildItem -Dir -Path "~\scoop\apps\flow-launcher\current" -Filter 'app*').FullName
Remove-Item -Path "$FLOW_HOME\UserData\Plugins\Reverso-Flow-*" -Force -Recurse
New-Item -Path "$FLOW_HOME\UserData\Plugins\Reverso-Flow-Dev" -ItemType Junction -Value $PWD\..\reverso-flow -Force

python311.exe -m pip install --upgrade pip
python311.exe -m pip install -r "./requirements.txt" -t "./lib"

Start-Process -FilePath "$FLOW_HOME\Flow.Launcher.exe"