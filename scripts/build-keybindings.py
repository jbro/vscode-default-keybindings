#!/usr/bin/env python3

import json
import re
import requests

defaultKeybindings = {
  'config.vscode-default-keybindings.removeOSKeybindings && isLinux': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/linux.negative.keybindings.json',
  'config.vscode-default-keybindings.removeOSKeybindings && isMac': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/macos.negative.keybindings.json',
  'config.vscode-default-keybindings.removeOSKeybindings && isWindows': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/windows.negative.keybindings.json',
  'config.vscode-default-keybindings.linuxKeybindings': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/linux.keybindings.json',
  'config.vscode-default-keybindings.macOSKeybindings': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/macos.keybindings.json',
  'config.vscode-default-keybindings.windowsKeybindings': 'https://raw.githubusercontent.com/codebling/vs-code-default-keybindings/master/windows.keybindings.json',
}

keybindings = []
version = ''

for expr, url in defaultKeybindings.items():

  print(f'Downloading  keybindings...')
  response = requests.get(url)
  response.raise_for_status()
  
  body = response.text

  # Extract version from comments
  comments = '\n'.join([ line for line in body.split('\n') if line.startswith('//') ])
  version = re.search(r'\d+\.\d+\.\d+', comments).group(0)

  # Remove comments
  body = re.sub(r'//.*\n', '', body)

  keymap = json.loads(body)
  
  for k in keymap:
    if 'when' in k:
      k['when'] = f'{expr} && ({k["when"]})'
    else:
      k['when'] = expr
    
    keybindings.append(k)

with open('package.json', 'r+') as f:
  package = json.load(f)
  
  package['version'] = version
  package['engines']['vscode'] = f'^{version}'
  package['contributes']['keybindings'] = keybindings
  
  f.seek(0)
  json.dump(package, f, indent=2)