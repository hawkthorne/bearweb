# Crash Reports

```lua
local sparkle = require 'sparkle'

sparkle.reportCrash("Hello?", {})
```

# Style

- All modules here should return top level tables that aren't 'Classes'.

# Metrics

# Auto-updating

These steps assume it's time for an update

## Windows

- Download the four needed files for the release into the working directory
  under new names
  - new_SDL.dll
  - new_OpenAL32.dll
  - new_DeVIL.dll
  - new_hawkthorne.exe
- Move the current items to a different name
  - old_SDL.dll
  - old_OpenAL32.dll
  - old_DeVIL.dll
  - old_hawkthorne.exe
- Now move all the new items to their expected location
- And relaunch the game

## OSX 

- Download the latest zipped app
- Unzip the app into the save game directory
- Remove the current app
- Move the freshly downloaded app to the old location
- Open it up

## appcast.json

```js
{
  "title": "Journey to the Center of Hawkthorne Appcast",
  "link": "http://files.projecthawkthorne.com/appcast.json",
  "description": "Most recent changes with links to updates.",
  "language": "en",
  "items": [{
    "title": "Version 0.0.84", 
    "published": "Sat, 03 Aug 2013 20:28:21 -0000",
    "version": "0.0.84",
    "platforms": [{
      "name": "macosx",
      "files": [{
        "url": "http://files.projecthawkthorne.com/releases/v0.0.84/hawkthorne-osx.zip",
        "length": 57980508
      }]
    },{
      "name": "windows",
      "files": [{
        "url": "http://files.projecthawkthorne.com/releases/v0.0.84/x86/DevIL.dll",
        "length": 730112
      },{
        "url": "http://files.projecthawkthorne.com/releases/v0.0.84/x86/SDL.dll",
        "length": 358912
      },{
        "url": "http://files.projecthawkthorne.com/releases/v0.0.84/x86/OpenAL32.dll",
        "length": 423424
      },{
        "url": "http://files.projecthawkthorne.com/releases/v0.0.84/x86/hawkthorne.exe",
        "length": 54379227
      }]
    }]
  }]
}
```
