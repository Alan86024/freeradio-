# -*- coding: utf-8 -*-
# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="freeradio",
	
	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	addon_summary=_("freeRadio: Radio and more"),
	
	# Add-on description
	# Translators: Long description to be shown for this add-on
	addon_description=_("""FreeRadio is an internet radio, podcast, audio-book, and local music add-on for NVDA that provides seamless access to thousands of internet radio stations via the Radio Browser open directory, RSS/Atom podcast feeds, the libriVox + GETEM digital library for the visually impaired, and your own local audio files and folders through its built-in jukebox. It features a fully accessible station browser with search, country filter, favourites management, and per-station, per-podcast, per-audio-book, and per-jukebox-track audio profiles. Podcast episodes, audio book chapters, and jukebox tracks resume automatically from where you left off - jukebox folders even pick up on the last track you were playing - with adjustable pitch-preserving playback speed and independent pitch-shift (semitone transpose). Playback is handled by BASS, with support for volume control, audio effects, output device selection, and simultaneous audio mirroring to a second device. Additional features include instant and scheduled recording, time-shift rewind of live radio, sleep and alarm timers, automatic ICY metadata announcements, Shazam-based music recognition, and a liked-songs log with lyrics lookup. All controls and shortcuts are designed for NVDA accessibility."""),
	
	# version
	addon_version="2026.24.2",
	
	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
## Added

### Jukebox
- **Bulk folder adding.** The Add Folder button in the Jukebox tab now lets you select several folders at once and adds them in a single operation, with one summary message reporting how many were added.

### Bulk mark-and-remove in every list tab
- In the **Favorites**, **Liked Songs**, **Audio Books**, and **Jukebox** lists you can now mark multiple items and remove them together:
  - Press **.** (period) on a highlighted item to mark or unmark it. Marked items show a "(marked)" suffix so their state stays visible while browsing.
  - Press **Delete** to remove every marked item at once. With nothing marked, Delete still removes only the focused item, as before.
  - A **Remove Selected** entry was added to each list's context menu, enabled only when at least one item is marked.
  - A single confirmation dialog summarises how many items will be removed before anything is deleted.

## Fixed

### Playback and resume
- **Live stations are no longer misclassified as podcasts on startup.** A live stream whose URL has no audio-file extension and no real saved podcast position entry is no longer resumed as if it were a podcast episode. This previously affected stations such as "AudioBook Radio", which showed an "Episode" field in the details dialog and was stuck behind the cassette resume-wait sound.

### Recording
- **Live stations whose Radio Browser tags contain "podcast" can be recorded again** with Ctrl+Win+E. Recording, and the resume/advance helpers in the playback pipeline, now key off the dedicated `media_kind` field instead of substring-matching the free-text `tags` field - which is community-assigned genre text a real live stream can legitimately carry.
- **TuneIn stations now record and capture song titles correctly.** Ctrl+Win+E recording and song capture previously wrote the tuning response to disk instead of the actual audio; they now resolve the tuning URL first, so recordings are valid and playable.

### Audio mirror
- **Audio mirror now works on stations whose server caps concurrent connections.** Main playback and the always-on time-shift buffer already use two connections; some servers reject a third for the mirror. If a mirror attempt fails and nothing is recording, the time-shift buffer's connection is freed and the mirror is retried once, then restored automatically when the mirror is stopped.
- Fixed a bug where `start_mirror()`'s internal cleanup (clearing a stale mirror engine before opening a new one) resumed the time-shift buffer prematurely, undoing the fix above on every repeat attempt.

### Jukebox
- **Jukebox folder playback no longer makes NVDA sluggish.** The volume/EQ/speed/transpose setup and the playback start now run on a background thread instead of NVDA's main thread, so the blocking BASS round-trips involved no longer stall speech and input during automatic track transitions.
- **Track audio profiles now survive path casing and form changes.** Profiles are keyed on the same normalised path form the entries list already uses, with a one-time migration on load, so a profile saved under one casing is still found when the same file is later referenced through a different one (case-insensitive filesystems, mapped drives).

### Music recognition
- **NVDA no longer feels sluggish while a Shazam recognition is running.** The pure-Python signature computation is CPU-heavy and, even though it already runs on a background thread, competed with NVDA's own thread for the GIL. The recognition thread's OS priority is now lowered and Python's GIL switch interval is temporarily shortened during signature computation, so NVDA's thread gets the CPU promptly. No change to recognition accuracy and negligible effect on recognition time.

### Timers and scheduled recordings
- **Pending sleep and alarm timers now survive add-on updates.** They are stored under NVDA's own config path instead of the add-on's install directory, which NVDA deletes and re-creates on every update.
- **Scheduled recordings now use the correct NVDA profile.** The scheduled-recordings store resolves through `globalVars.appArgs.configPath` instead of `%APPDATA%\nvda`, so a portable NVDA copy or an `nvda.exe -c <path>` session writes to and reads from its own profile instead of the installed one.
- Fixed a race where a timer added between the timer loop's wakeup clear and its wait could be delayed by up to a full minute.

### Persistence
- **User data is now written atomically** (temp file plus `os.replace()`) for favourites, timers, podcast resume positions, jukebox folder positions, and the jukebox library, so a crash or power loss mid-write can no longer leave a corrupted file behind.

### UI, translations and small fixes
- `recorder.py` now calls `addonHandler.initTranslation()`, so `_()` resolves against FreeRadio's own translation catalog.
- Removed a dead `globalVars.appArgs.secure` guard that never took effect, and fixed an unbalanced `prePopup()` on the first dialog open.
- Fixed a "potcasts" typo in the time-shift checkbox label.
- Removed a stray "()" from the auto-generated per-favourite shortcut descriptions in NVDA's Input Gestures dialog.
- Removed a duplicate "S" in the Turkish sort-order table (`_TR_ORDER`) that shifted the sort key for every character after it.
"""),
	
	# Author(s)
	addon_author="Çağrı Doğan <cagrid@hotmail.com>",
	
	# URL for the add-on documentation support
	addon_url="https://github.com/Surveyor123/freeradio",
	
	# URL for the add-on repository where the source code can be found
	addon_sourceURL="https://github.com/Surveyor123/freeradio",
	
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
pythonSources: list[str] = ["addon/globalPlugins/freeradio/*.py"]

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