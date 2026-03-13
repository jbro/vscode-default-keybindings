#!/usr/bin/env python3

import json
import re

defaultKeybindings = {
  'config.vscode-default-keybindings.removeOSKeybindings && isLinux': 'vs-code-default-keybindings/linux.negative.keybindings.json',
  'config.vscode-default-keybindings.removeOSKeybindings && isMac': 'vs-code-default-keybindings/macos.negative.keybindings.json',
  'config.vscode-default-keybindings.removeOSKeybindings && isWindows': 'vs-code-default-keybindings/windows.negative.keybindings.json',
  'config.vscode-default-keybindings.linuxKeybindings': 'vs-code-default-keybindings/linux.keybindings.json',
  'config.vscode-default-keybindings.macOSKeybindings': 'vs-code-default-keybindings/macos.keybindings.json',
  'config.vscode-default-keybindings.windowsKeybindings': 'vs-code-default-keybindings/windows.keybindings.json',
}

keybindings = []
keybinding_counts = {}
version = ''

def get_fingerprint(binding):
    return json.dumps(binding, sort_keys=True)

for expr, path in defaultKeybindings.items():
    with open(path, 'r') as f:
        r = f.read()
        # Remove comments
        r = re.sub(r'//.*\n', '', r)
        # Parse keybindings
        keymap = json.loads(r)
        # Generate fingerprints and count
        for binding in keymap:
            fingerprint = get_fingerprint(binding)
            if fingerprint not in keybinding_counts:
                keybinding_counts[fingerprint] = 0
            keybinding_counts[fingerprint] += 1

for expr, path in defaultKeybindings.items():

  # Open keybindings file
  with open(path, 'r') as f:

    # Read file
    r = f.read()

    # Extract version from comments
    comments = '\n'.join([ line for line in r.split('\n') if line.startswith('//') ])
    version = re.search(r'\d+\.\d+\.\d+', comments).group(0)

    # Remove comments
    r = re.sub(r'//.*\n', '', r)

    # Parse keybindings
    keymap = json.loads(r)

    # Update keybindings
    for k in keymap:
      fingerprint = get_fingerprint(k)
      # Skip if fingerprint appears in all three platforms
      if keybinding_counts.get(fingerprint, 0) == 3:
        continue
          
      if 'when' in k:
        k['when'] = f'{expr} && ({k["when"]})'
      else:
        k['when'] = expr

      keybindings.append(k)

# Update package.json
with open('package.json', 'r+', encoding='utf-8') as f:
  package = json.load(f)

  package['engines']['vscode'] = f'^{version}'
  package['contributes']['keybindings'] = keybindings

  f.seek(0)
  json.dump(package, f, ensure_ascii=False, indent=4)
  f.write('\n')
  f.truncate()
