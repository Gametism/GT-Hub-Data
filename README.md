# GameFocus-Data

The shared list for [GameFocus](https://github.com/Gametism). GameFocus reads `gamefocus-data.txt` from this repository once a day at most, together with its graphics driver check.

It holds what GameFocus cannot find out by itself and what is the same for everybody.

## What is in it

**`[hotfix]`** NVIDIA publishes its hotfix drivers only as support articles, so GameFocus cannot see them. A line here, and GameFocus tells its users that the hotfix driver is out, with a warning before NVIDIA's article opens.

```
maker | version | based on | date | page at the maker | what it fixes
nvidia | 621.31 | 621.24 | 2026-11-20 | https://nvidia.custhelp.com/app/answers/detail/a_id/0000 | G-SYNC flicker in two games
```

- `maker`: `nvidia`, `amd` or `intel`
- `based on` and `date`: `-` when not known; the date as `YYYY-MM-DD`
- the page has to be at the maker: `nvidia.custhelp.com`, `www.nvidia.com`, `www.amd.com`, `www.intel.com`
- `what it fixes` may be left out

A hotfix driver is named only while it is newer than the installed driver and newer than the newest regular driver. Old lines do no harm.

**`[arguments]`** Launch arguments that were tried and work, for a game or for an engine. GameFocus offers them in a game's More menu > Launch Arguments.

```
which game | the argument(s) | what it does
steam:49520 | -NoLauncher | Skip The Launcher
exe:twfc.exe | -nosplash | No Splash Picture At The Start
engine:ue3 | -nostartupmovies | Skip The Intro Movies
```

- `which game`: `steam:` and the game's Steam number, `exe:` and its exe's file name, or `engine:` with `ue3`, `ue4`, `unity` or `source`
- the arguments as they stand behind the exe; several that belong together go in one line
- `what it does`: a few words

More sections come with the GameFocus features that use them. A GameFocus that does not know a section passes it over.

## What GameFocus does with it

It reads the file and keeps a copy. Nothing in the file is run. A page it names is opened only at the maker of the driver, and only when the user clicks.

## Suggestions

Open an issue. GameFocus does that for launch arguments: "Suggest For Everyone" in the Launch Arguments window opens one that is already filled in.
