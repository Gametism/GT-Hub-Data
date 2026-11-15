# GT-Hub-Data

The shared list for [GT-Hub](https://github.com/Gametism) (called Sidewarden up to version 0.11.22, and GameFocus up to 0.10.35). GT-Hub reads `gt-hub-data.txt` from this repository once a day at most, together with its graphics driver check.

`sidewarden-data.txt` is a copy of it, for the versions that read the list under its old name (Sidewarden 0.11.0 to 0.11.22, GT-Hub 0.11.23). It is made by itself whenever `gt-hub-data.txt` changes (`.github/workflows/copy-for-older-versions.yml`), so only `gt-hub-data.txt` is edited. Links to `Gametism/Sidewarden-Data` lead here too: GitHub forwards them since the repository was renamed.

It holds what GT-Hub cannot find out by itself and what is the same for everybody.

## What is in it

**`[hotfix]`** NVIDIA publishes its hotfix drivers only as support articles, so GT-Hub cannot see them. A line here, and GT-Hub tells its users that the hotfix driver is out, with a warning before NVIDIA's article opens.

```
maker | version | based on | date | page at the maker | what it fixes
nvidia | 621.31 | 621.24 | 2026-11-20 | https://nvidia.custhelp.com/app/answers/detail/a_id/0000 | G-SYNC flicker in two games
```

- `maker`: `nvidia`, `amd` or `intel`
- `based on` and `date`: `-` when not known; the date as `YYYY-MM-DD`
- the page has to be at the maker: `nvidia.custhelp.com`, `www.nvidia.com`, `www.amd.com`, `www.intel.com`
- `what it fixes` may be left out

A hotfix driver is named only while it is newer than the installed driver and newer than the newest regular driver. Old lines do no harm.

**`[arguments]`** Launch arguments that were tried and work, for a game or for an engine. GT-Hub offers them in a game's More menu > Launch Arguments.

```
which game | the argument(s) | what it does
steam:49520 | -NoLauncher | Skip The Launcher
exe:twfc.exe | -nosplash | No Splash Picture At The Start
engine:ue3 | -nostartupmovies | Skip The Intro Movies
```

- `which game`: `steam:` and the game's Steam number, `exe:` and its exe's file name, or `engine:` with `ue3`, `ue4`, `unity` or `source`
- the arguments as they stand behind the exe; several that belong together go in one line
- `what it does`: a few words

**`[affinity]`** Older games that fail on a processor with many cores and run when they get fewer. GT-Hub gives a game on this list its cores by itself (a game's More menu > CPU Cores shows it).

```
which game | cores | why | fixed by | only beside
steam:10150 | 8 | Prototype crashes with more than 8 logical processors
exe:avatar.exe | 8 | Crashes at its start with many threads | AVATAR-AdvancedConfigurator.* | Dunia.dll
```

- `which game`: `steam:` and the game's Steam number, or `exe:` and its exe's file name
- `cores`: how many the game gets, 1 to 64
- `why`: what happens with all cores, in a few words
- `fixed by` (may be left out): what repairs the game already, so that GT-Hub stands back. `steam` for a Steam release that needs nothing, or file names next to the exe (`*` allowed, several with commas), such as a mod's settings file
- `only beside` (may be left out): the line counts only for the game that has this file next to its exe, for an exe name other games have too

Only games where fewer cores are known to help belong here. A game that is repaired by a changed exe does not.

More sections come with the GT-Hub features that use them. A version that does not know a section passes it over.

## What GT-Hub does with it

It reads the file and keeps a copy. Nothing in the file is run. A page it names is opened only at the maker of the driver, and only when the user clicks.

## Suggestions

Open an issue. GT-Hub does that for launch arguments and CPU cores: "Suggest For Everyone" in the Launch Arguments window and in More > CPU Cores opens one that is already filled in.

A suggestion is taken into `gt-hub-data.txt` (and its copy) by itself (`.github/workflows/add-suggestion.yml`):

- at once when the repository's owner opened it,
- otherwise once it has the label `approved` (only the owner and collaborators can label an issue, so nothing gets into everybody's GT-Hub that nobody looked at).

The line under "Line for the list:" is checked by the same rules GT-Hub reads the list with (where it still says "(what it does)", what was written under "What they do" takes its place). A line that breaks one gets a comment that says which, and the issue stays open: edit the line and it is taken over. A line that is taken over gets a comment, the issue is closed, and every GT-Hub offers it within a day.
