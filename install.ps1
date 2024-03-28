Set-Variable -Name "FLOW_HOME" (Get-ChildItem -Dir -Path "~\scoop\apps\flow-launcher\current" -Filter 'app*').FullName
taskkill /f /im Flow*

$tag = (Invoke-RestMethod -Uri https://api.github.com/repos/CoDen256/reverso-flow/releases/latest).tag_name
Invoke-WebRequest https://github.com/CoDen256/reverso-flow/releases/latest/download/Reverso-Flow-$tag.zip -OutFile ~\Downloads\Reverso-Flow-$tag.zip
Remove-Item "$FLOW_HOME\UserData\Plugins\Reverso-Flow-*" -Recurse -Force
Expand-Archive -Path ~\Downloads\Reverso-Flow-$tag.zip -DestinationPath "$FLOW_HOME\UserData\Plugins\Reverso-Flow-$tag"
Remove-Item -Path ~\Downloads\Reverso-Flow-$tag.zip


Start-Process -FilePath "$FLOW_HOME\Flow.Launcher.exe"
