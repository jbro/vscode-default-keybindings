#!/usr/bin/env python3

import json
import re

defaultKeybindings = [
  {
    'expr': 'config.vscode-default-keybindings.removeOSKeybindings && isLinux',
    'path': 'vs-code-default-keybindings/linux.negative.keybindings.json',
    'platform': 'linux',
    'mode': 'negative',
  },
  {
    'expr': 'config.vscode-default-keybindings.removeOSKeybindings && isMac',
    'path': 'vs-code-default-keybindings/macos.negative.keybindings.json',
    'platform': 'macos',
    'mode': 'negative',
  },
  {
    'expr': 'config.vscode-default-keybindings.removeOSKeybindings && isWindows',
    'path': 'vs-code-default-keybindings/windows.negative.keybindings.json',
    'platform': 'windows',
    'mode': 'negative',
  },
  {
    'expr': 'config.vscode-default-keybindings.linuxKeybindings',
    'path': 'vs-code-default-keybindings/linux.keybindings.json',
    'platform': 'linux',
    'mode': 'positive',
  },
  {
    'expr': 'config.vscode-default-keybindings.macOSKeybindings',
    'path': 'vs-code-default-keybindings/macos.keybindings.json',
    'platform': 'macos',
    'mode': 'positive',
  },
  {
    'expr': 'config.vscode-default-keybindings.windowsKeybindings',
    'path': 'vs-code-default-keybindings/windows.keybindings.json',
    'platform': 'windows',
    'mode': 'positive',
  },
]

keybindings = []
version = ''
platforms = {'linux', 'macos', 'windows'}

def getFingerprint(binding):
  return json.dumps(binding, sort_keys=True)

def loadKeymap(path):
  with open(path, 'r') as f:

    # Read file
    r = f.read()

    # Extract version from comments
    comments = '\n'.join([ line for line in r.split('\n') if line.startswith('//') ])
    match = re.search(r'\d+\.\d+\.\d+', comments)

    # Remove comments
    r = re.sub(r'//.*\n', '', r)

    # Parse keybindings
    return json.loads(r), match.group(0) if match else ''

fingerprints = {}

for entry in defaultKeybindings:
  keymap, _ = loadKeymap(entry['path'])
  modeFingerprints = fingerprints.setdefault(entry['mode'], {})

  for binding in keymap:
    bindingPlatforms = modeFingerprints.setdefault(getFingerprint(binding), set())
    bindingPlatforms.add(entry['platform'])

commonFingerprints = {
  mode: { fingerprint for fingerprint, bindingPlatforms in modeFingerprints.items() if bindingPlatforms == platforms }
  for mode, modeFingerprints in fingerprints.items()
}

for entry in defaultKeybindings:

  # Open keybindings file
  keymap, keymapVersion = loadKeymap(entry['path'])
  if keymapVersion:
    version = keymapVersion

  # Update keybindings
  for k in keymap:
    if getFingerprint(k) in commonFingerprints[entry['mode']]:
      continue

    if 'when' in k:
      k['when'] = f'{entry["expr"]} && ({k["when"]})'
    else:
      k['when'] = entry['expr']

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
