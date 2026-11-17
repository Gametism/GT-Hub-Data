# GT-Hub-Data

The shared list for [GT-Hub](https://github.com/Gametism) (called Sidewarden up to version 0.11.22, and GameFocus up to 0.10.35). GT-Hub reads `gt-hub-data.txt` from this repository: from version 0.11.50 on at its start and every three hours, up to 0.11.49 once a day together with its graphics driver check (and not at all while that check was switched off).

It is also where GT-Hub gets RenderToggler from (see [RenderToggler](#rendertoggler) below).

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

**`[supporters]`** The supporters on Patreon, thanked by name in About GT-Hub (GT-Hub 0.11.58 and newer). It is written by itself once a day from Patreon (`.github/workflows/patreon-supporters.yml`), the highest tier first and in a tier the longest supporters first - so it is not edited here.

```
name | tier
Jane D. | Legend
Kai
```

- How a supporter is named, and who is left out, is set in `supporters-names.txt`: `Jane D.` (first name and initial) unless it says otherwise, `-` for someone who does not want to be named
- Until Patreon is connected the workflow does nothing. Connecting it once: a client in Patreon's developer portal (`patreon.com/portal/registration/register-clients`, API version 2), its Client ID, Client Secret, Creator's Access Token and Creator's Refresh Token as the secrets `PATREON_CLIENT_ID`, `PATREON_CLIENT_SECRET`, `PATREON_ACCESS_TOKEN` and `PATREON_REFRESH_TOKEN`, and a fine-grained token for this repository with "Secrets: Read and write" as `SECRETS_TOKEN` - Patreon renews its tokens after some weeks, and the new ones are kept in the secrets with it. Then Actions > Patreon supporters > Run workflow.

More sections come with the GT-Hub features that use them. A version that does not know a section passes it over.

## RenderToggler

GT-Hub 0.11.50 and newer fetch RenderToggler from the releases of this repository and bring every game that has GT-Hub's RenderToggler to the newest build by themselves: the window when it looks at its lists (within the hour), the tray helper every three hours while the window stays closed. Never into a game that is running, and never over a copy someone put into a game themselves.

**A new build:**

1. Releases > Draft a new release.
2. A tag that starts with `RenderToggler`, such as `RenderToggler-1.0.0-EF447` (letters, digits and `. - _ +` only).
3. Drag in the files of the build's `GT-Hub` folder: `RenderToggler.addon64`, `RenderToggler.addon`, the license texts and `RenderToggler.txt`.
4. Publish release.

GT-Hub's `tools\publish_rendertoggler.cmd` does the same: drag the build's `GT-Hub` folder onto it. It makes the release with the GitHub CLI where that is signed in, and otherwise opens the filled-in release page and the folder.

On GitHub the release is shown as just "RenderToggler", whatever title it was published with: the workflow below sets the title, and an empty text becomes one short line without a version. The version stays in the tag (a new one for every release) and in the list GT-Hub reads.

A minute after the release is published, `.github/workflows/rendertoggler.yml` writes `RenderToggler/RenderToggler.txt`: the version (from the build's `RenderToggler.txt`, otherwise the tag), the release the files are in, and every file with its SHA-256, worked out from the files themselves. GT-Hub takes only files that match it, and only from a release of this repository. Deleting the newest release takes the list back to the one before; drafts and pre-releases do not count.

Nothing of RenderToggler's source is in this repository.

## What GT-Hub does with it

It reads the file and keeps a copy. Nothing in the file is run. A page it names is opened only at the maker of the driver, and only when the user clicks.

## Suggestions

Open an issue. GT-Hub does that for launch arguments and CPU cores: "Suggest For Everyone" in the Launch Arguments window and in More > CPU Cores opens one that is already filled in.

A suggestion is taken into `gt-hub-data.txt` (and its copy) by itself (`.github/workflows/add-suggestion.yml`):

- at once when the repository's owner opened it,
- otherwise once it has the label `approved` (only the owner and collaborators can label an issue, so nothing gets into everybody's GT-Hub that nobody looked at).

The line under "Line for the list:" is checked by the same rules GT-Hub reads the list with (where it still says "(what it does)", what was written under "What they do" takes its place). A line that breaks one gets a comment that says which, and the issue stays open: edit the line and it is taken over. A line that is taken over gets a comment, the issue is closed, and every GT-Hub offers it within a day.
