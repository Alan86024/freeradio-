# -*- coding: utf-8 -*-
# FreeRadio - Explorer app module.
#
# Goes in the add-on's appModules/ folder (a sibling of globalPlugins/, at
# the add-on package root - NOT inside globalPlugins/freeradio/), named
# explorer.py so NVDA loads it only while the focused window belongs to
# explorer.exe.
#
# This replaces ExplorerIntegrationMixin/explorerIntegrationMixin.py, which
# lived on GlobalPlugin and therefore registered its two gestures globally
# - functionally fine once bound (the appModule.appName=="explorer" runtime
# check + gesture.send() fallback made it act correctly everywhere), but
# NVDA's Input Help mode reports a *global* gesture's binding regardless of
# where you are (it reads the gesture map, it doesn't run the script), so
# pressing the assigned keys in input help mode announced these commands in
# every application, not just Explorer.
#
# An AppModule's scripts/gestures are only part of NVDA's active gesture
# map while the focused window's owning process matches this module's name
# (explorer.exe here) - so both the actual binding *and* what Input Help
# mode reports are now correctly scoped to explorer.exe, with no runtime
# forwarding needed for the "wrong app entirely" case. The windowClassName/
# role check below still narrows that down further, to just the file-list
# control (not the address bar, tree view, ribbon, or search box) - NVDA
# has no finer-grained scoping than "this process", and explorer.exe hosts
# all of those plus the taskbar (and, on some Windows versions, the
# desktop). One known overlap this doesn't (and can't cleanly) rule out:
# the classic desktop icon view is also a SysListView32 list of LISTITEMs
# owned by explorer.exe, so these two gestures work there too - almost
# certainly harmless (playing/jukebox-adding a file focused on the desktop
# is exactly the same operation), but worth knowing about.
#
# Because this is a different scriptable object than GlobalPlugin, any
# gesture assigned to the old GlobalPlugin-based scripts does NOT carry
# over automatically - re-assign "." / "," (or whatever you used) from
# NVDA's Input Gestures dialog *while focused inside an Explorer window*;
# they'll appear under this app's own section (labelled with the running
# application's name) rather than under "All applications".

import os

import nvdaBuiltin.appModules.explorer
import controlTypes
import ui
import winUser
from scriptHandler import script

import addonHandler
addonHandler.initTranslation()
_tr = globals()["_"]
_ = _tr
del _tr

from globalPlugins.freeradio import jukebox


def _get_freeradio_plugin():
	"""Find the running FreeRadio GlobalPlugin instance, so this app
	module's scripts can reach its self._play_station() the same way
	GlobalPlugin's own mixins do via self. Imports GlobalPlugin lazily
	(inside the function, not at module load time) since appModules can
	load before global plugins have necessarily finished initialising -
	mirrors the reasoning behind this add-on's existing lazy
	_get_freeradio_plugin() helper in settingsPanel.py (see the comment
	there); reimplemented locally here rather than imported from it to
	keep this app module self-contained and independent of
	settingsPanel.py's own import chain."""
	import globalPluginHandler
	from globalPlugins.freeradio import GlobalPlugin as FreeRadioGlobalPlugin
	for plugin in globalPluginHandler.runningPlugins:
		if isinstance(plugin, FreeRadioGlobalPlugin):
			return plugin
	return None


def _get_explorer_list_item_path():
	"""Return the absolute path of the file/folder currently focused in
	Explorer's file-list view, or None if the current focus isn't one
	(address bar, tree view, ribbon, search box, taskbar, desktop icon
	view aside - see the module docstring's note on that last one).

	No appModule.appName check needed here (unlike the GlobalPlugin
	version this replaced) - NVDA only routes focus in explorer.exe to
	this module's scripts in the first place. windowClassName
	("SysListView32" for the classic Details/Icons view, "DirectUIHWND"
	confirmed by testing to be what the user's Explorer actually uses)
	plus role LISTITEM is what narrows it down to the file list itself.

	Path resolution goes through comtypes (bundled with NVDA) to drive
	Shell.Application COM automation - not win32com.client, confirmed
	during testing to be absent from the pywin32 subset NVDA ships (see
	_sapi5_speak() in __init__.py, which already preferred comtypes for
	the same reason). The focused Explorer window is matched to the
	right entry in Shell.Application's Windows() collection via
	winUser.getAncestor(..., winUser.GA_ROOT) - NVDA's own core wrapper,
	not win32gui.GetAncestor: confirmed by a real crash report that
	win32gui isn't part of the pywin32 subset bundled with older NVDA
	releases (2024.1/2025.1 - ModuleNotFoundError: No module named
	'win32gui'; fine on 2026.2, where it apparently is bundled), so
	depending on it broke this script entirely on those versions.
	winUser is NVDA core itself, not a pywin32 wrapper, so it's
	guaranteed present on every supported version - it's also what
	NVDA's own built-in appModules/explorer.py uses internally for this
	exact ancestor-window lookup, and already returns the correctly
	sign-extended 64-bit HWND (the same truncation bug class as
	bass_host.py's BASS_ChannelGetPosition needing an explicit c_int64
	restype - actually hit and fixed while building this - would apply
	to a raw, untyped ctypes.windll.user32.GetAncestor call, but not to
	winUser's own wrapper, which already declares the right restype)."""
	import api
	focus = api.getFocusObject()
	if not focus:
		return None
	if focus.windowClassName not in ("SysListView32", "DirectUIHWND"):
		return None
	if focus.role != controlTypes.Role.LISTITEM:
		return None

	try:
		root_hwnd = winUser.getAncestor(focus.windowHandle, winUser.GA_ROOT)
	except Exception:
		return None
	if not root_hwnd:
		return None

	try:
		import comtypes.client
		shell = comtypes.client.CreateObject("Shell.Application")
		windows = shell.Windows()
		# Indexed Count/Item(i) access rather than a Python "for window in
		# windows:" loop - see _list_sapi5_voices()/_speak()'s comtypes
		# branch in __init__.py, which do the same for SAPI's voice
		# collection: comtypes' dynamic dispatch wrapper doesn't support
		# Python's iteration protocol directly.
		for i in range(windows.Count):
			try:
				window = windows.Item(i)
				if window.HWND != root_hwnd:
					continue
				item = window.Document.FocusedItem
				if item is None:
					return None
				return item.Path
			except Exception:
				continue
	except Exception:
		return None
	return None


class AppModule(nvdaBuiltin.appModules.explorer.AppModule):

	@script(
		# Translators: Name of an NVDA command; plays the audio file focused in Windows Explorer with FreeRadio, without needing it to already be in the jukebox library.
		description=_("Play the focused file with FreeRadio"),
		category=_("FreeRadio"),
	)
	def script_explorerPlayFile(self, gesture):
		path = _get_explorer_list_item_path()
		plugin = _get_freeradio_plugin()
		if path is None or plugin is None:
			gesture.send()
			return

		if os.path.isdir(path):
			# Deliberately out of scope - see explorerIntegrationMixin.py's
			# matching comment (same reasoning: folder auto-advance needs
			# the folder to already be a persisted JukeboxManager entry).
			# Translators: Spoken when the "play focused item" Explorer shortcut is used on a folder rather than a file.
			ui.message(_("This is a folder. Playing only works for files - add it to the jukebox to play the whole folder."))
			return
		if os.path.splitext(path)[1].lower() not in jukebox.AUDIO_EXTENSIONS:
			# Translators: Spoken when the "play focused item" Explorer shortcut is used on a file that isn't a recognized audio format.
			ui.message(_("Not a recognized audio file."))
			return

		manager = jukebox.JukeboxManager()
		track = jukebox.JukeboxTrack(path)
		station_dict = track.to_dict()
		profile = manager.get_track_profile(path)
		if profile:
			station_dict["station_audio"] = profile
		plugin._play_station(station_dict)


	@script(
		# Translators: Name of an NVDA command; adds the file or folder focused in Windows Explorer to the FreeRadio jukebox.
		description=_("Add the focused item to the FreeRadio jukebox"),
		category=_("FreeRadio"),
	)
	def script_explorerAddToJukebox(self, gesture):
		path = _get_explorer_list_item_path()
		if path is None:
			gesture.send()
			return

		manager = jukebox.JukeboxManager()
		if os.path.isdir(path):
			entry, error = manager.add_folder(path)
		else:
			entry, error = manager.add_file(path)

		if error:
			ui.message(error)
			return
		# Translators: Spoken after successfully adding an Explorer file or folder to the jukebox; %s is its display title.
		ui.message(_("Added to jukebox: %s") % entry.title)