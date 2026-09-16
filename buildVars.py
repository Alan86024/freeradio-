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
	addon_version="2026.24.1",
	
	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
## Fixed
- **Wrong duration/bitrate/sample rate/channels for some MP3s** (e.g. showing 12:44 instead of 4:46, mono instead of stereo, 32 kbps / 8 kHz instead of the real values). Caused by a missing entry in the MPEG bitrate table for Version 2/2.5 Layer III files (common for lower sample-rate MP3s), which made frame detection fail and lock onto random bytes elsewhere in the file.
- **VBR files could report the placeholder bitrate** of the dummy "Xing"/ "Info"/"VBRI" header frame instead of the track's real average bitrate.
- **Files without an ID3v2 tag could be probed from the wrong byte offset**, throwing off duration/bitrate/sample rate/channel detection.
## Added
- **Jukebox folders now resume from the last track played**, not always track 1. The track index is remembered per folder (new `jukebox_folder_positions.json`, alongside the existing `podcast_positions.json`) and updated every time a track starts playing as part of a folder sequence - including automatic advance while the dialog is closed. Cleared once the folder is played through to its last track, so it starts over next time; also cleared if the folder is removed from the jukebox library.
- An explicit selection already made in the tracks list still wins over the remembered position - this only kicks in when nothing's selected.
- Within-track resume position (the existing per-file feature) applies on top of this automatically, so the resumed track picks up mid-song too.
## Changed
- Playing a folder (or a single file) now updates the tracks list's selection to the track that actually starts playing, without moving keyboard focus there.
## Added
- The tracks list selection now also follows the playing track when it changes on its own: a track finishing and auto-advancing to the next one, or a Ctrl+Win+J/K seek crossing into a different track. Only updates if the folder being advanced is the one currently shown in the tracks list; never moves keyboard focus.
## Fixed
- Playing a jukebox track (single file or folder) no longer requires an internet connection. The connectivity check in `_play_station()` now skips jukebox tracks (`media_kind == "jukebox"`), since they're local files and never touch the network.
## Fixed
- Time-shift (rewind) now works on stations that use a "redirect" style address, such as many TuneIn stations. Previously, time-shift would try to reconnect over and over without ever actually buffering anything, so rewind wasn't available on those stations - even though normal playback worked fine. Regular listening was never affected.
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