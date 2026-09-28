# -*- coding: utf-8 -*-
# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="freeAudio",
	
	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	addon_summary=_("freeAudio: Radio and more"),
	
	# Add-on description
	# Translators: Long description to be shown for this add-on
	addon_description=_("""freeAudio is an internet radio, podcast, audio-book, and local music add-on for NVDA that provides seamless access to thousands of internet radio stations via the Radio Browser open directory, RSS/Atom podcast feeds, the libriVox + GETEM digital library for the visually impaired, and your own local audio files and folders through its built-in jukebox. It features a fully accessible station browser with search, country filter, favourites management, and per-station, per-podcast, per-audio-book, and per-jukebox-track audio profiles. Podcast episodes, audio book chapters, and jukebox tracks resume automatically from where you left off - jukebox folders even pick up on the last track you were playing - with adjustable pitch-preserving playback speed and independent pitch-shift (semitone transpose). Playback is handled by BASS, with support for volume control, audio effects, output device selection, and simultaneous audio mirroring to a second device. Additional features include instant and scheduled recording, time-shift rewind of live radio, sleep and alarm timers, automatic ICY metadata announcements, Shazam-based music recognition, and a liked-songs log with lyrics lookup. All controls and shortcuts are designed for NVDA accessibility."""),
	
	# version
	addon_version="2026.25.0",
	
	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
# freeAudio: What's New

## FreeRadio is now freeAudio

- Your settings, favourites, podcasts, jukebox library and recordings location are carried over automatically on first start.
- Custom shortcuts assigned in Input Gestures must be set again.
- Uninstall the old FreeRadio add-on to avoid conflicts.

## Added

### Favourite groups (folders)

- **M3U import:** reads the `group-title` attribute. If only the first station in a folder carries the tag, as common exporters such as DVBViewer write it, the group is carried forward to the stations that follow.
- **M3U export:** writes `group-title` again, so a round trip through freeAudio no longer drops the folder structure. JSON import and export keep the same group field.
- **List display:** each favourite shows its folder as a trailing "— Group" suffix. This is display only, and the station's name is never changed.
- **Filter box:** now also matches the group and splits your text on whitespace, so each word can match a different field. For example, "Houston Classical" finds "Houston Public Media Classical", even though that phrase never appears in one piece.
- **Assign to Group…** (new context-menu command): mark favourites with `.`, then type a group name to organise them by hand, or leave the name empty to clear the group. It works for hand-made favourites too, not only imported M3U ones.
- **Backward compatible:** favourites without a group default to an empty group, and the list looks and behaves exactly as before until you import a grouped playlist or use Assign to Group.

### Mark a range of items

Favourites, Liked Songs, Audio Books and Jukebox already let you mark single rows with `.` for bulk removal. You can now mark whole ranges:

- **Shift+End:** marks or unmarks from the focused row to the last row.
- **Shift+Home:** marks or unmarks from the focused row to the first row.

The focused row's current state decides the direction: if it is unmarked, the whole range gets marked, and if it is marked, the whole range gets unmarked. This mirrors how Shift+Home and Shift+End extend a selection in a text field. Afterwards focus moves to the far end of the range and the number of rows changed is announced. The placeholder rows in Liked Songs ("No liked songs yet.", "No results found.") are never marked.

### Timers

- New **recurring** option for timers.

### Windows Explorer integration

A new `appModules/explorer.py`, active only in the file list of `explorer.exe`, not in the address bar, tree view, ribbon, search box or other Explorer controls. It adds two commands, both unassigned by default:

- **Play the focused file with freeAudio**
- **Add the focused file or folder to the freeAudio jukebox**

Assign a key (for example `.` or `,`) in Input Gestures while focused in Explorer. It is bound only there and still works as itself everywhere else.

## Fixed

- **The freeAudio window sometimes failed to come to the foreground**, requiring an NVDA restart. If you minimized the window instead of closing it, it stayed in the taskbar and could not be brought back. Reopening it now restores a minimized window before raising it.
"""),
	
	# Author(s)
	addon_author="Çağrı Doğan <cagrid@hotmail.com>",
	
	# URL for the add-on documentation support
	addon_url="https://github.com/Surveyor123/freeAudio",
	
	# URL for the add-on repository where the source code can be found
	addon_sourceURL="https://github.com/Surveyor123/freeAudio",
	
	# Documentation file name
	addon_docFileName="readme.html",
	
	# Minimum NVDA version supported
	addon_minimumNVDAVersion="2025.1.0",
	
	# Last NVDA version supported/tested
	addon_lastTestedNVDAVersion="2026.2.0",
	
	# Add-on update channel (None denotes stable releases)
	addon_updateChannel=None,
	
	# Add-on license
	addon_license="GPL-2.0",
	addon_licenseURL=None,
)

# Define the python files that are the sources of your add-on.
# We point to the specific directory where your code lives.
pythonSources: list[str] = [
	"addon/globalPlugins/freeAudio/*.py",
	"addon/appModules/*.py",
]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
excludedFiles: list[str] = []

# Base language for the NVDA add-on
# Since your code strings (e.g. _("Table")) are in English, we keep this as "en".
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
markdownExtensions: list[str] = []

# Custom braille translation tables
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}