# -*- coding: utf-8 -*-
# FreeRadio - Instant/song-capture recording toggle, recordings folder,
# and podcast episode download
#
# Extracted from GlobalPlugin in __init__.py. Mixed into GlobalPlugin, so
# `self` here is a GlobalPlugin instance - self._player and self._recorder
# (defined elsewhere on GlobalPlugin) are used as normal instance
# attributes via the class's MRO, no import needed for those.
#
# NOTE: every script here with a default gesture= must also be listed in
# GlobalPlugin's __gestures dict in __init__.py (see the __gestures
# comment there for why).

import logging
import os
import threading
import config
import ui
import wx
from scriptHandler import script, getLastScriptRepeatCount

import addonHandler
addonHandler.initTranslation()
_tr = globals()["_"]
_ = _tr
del _tr

from . import _notify

log = logging.getLogger(__name__)


class RecordingMixin:
	"""Instant/song-capture recording toggle (Ctrl+Win+E), the recordings
	folder shortcut, and podcast episode download (used by
	script_addToFavorites when a podcast episode is playing)."""

	def _download_current_podcast_episode(self, station):
		"""Download the currently playing podcast episode, used by
		Ctrl+Win+V in place of "add to favourites" when a podcast episode
		(rather than a radio station) is playing. Works regardless of
		whether the browser dialog is open."""
		# Translators: Fallback episode title used for the downloaded filename if the currently playing episode has no name.
		title = station.get("name", "").strip() or _("Episode")
		url = station.get("url") or station.get("url_resolved")
		if not url:
			# Translators: Spoken when trying to download the current podcast episode but it has no resolvable URL.
			ui.message(_("This episode has no downloadable URL."))
			return

		from . import podcast
		out_path, filename = podcast.episode_download_target(title, url)
		if os.path.exists(out_path):
			# Translators: Spoken when the episode was already downloaded before; %s is the existing filename. Same wording as the Podcasts tab download action.
			ui.message(_("File already exists: %s") % filename)
			return

		# Translators: Spoken when the Ctrl+Win+V episode download starts; %s is the episode title.
		ui.message(_("Downloading: %s") % title)

		def _do_download():
			try:
				podcast.download_episode_file(url, out_path)
				# Translators: Spoken when the Ctrl+Win+V episode download finishes; %s is the saved filename.
				wx.CallAfter(ui.message, _("Download complete: %s") % filename)
			except Exception as e:
				# Translators: Spoken when the Ctrl+Win+V episode download fails; %s is the underlying error.
				wx.CallAfter(ui.message, _("Download failed: %s") % str(e))

		threading.Thread(target=_do_download, daemon=True).start()

	@script(
		# Translators: Name of an NVDA command (Ctrl+Win+E); single-press toggles a plain instant recording, double-press toggles song-capture recording instead - see this method's logic below.
		description=_("Start or stop instant recording"),
		category=_("FreeRadio"),
		gesture="kb:control+windows+e",
	)
	def script_toggleRecord(self, gesture):
		# Always cancel any pending delayed action so that only the latest press counts.
		old_timer = getattr(self, "_record_action_timer", None)
		if old_timer:
			old_timer.Stop()
			self._record_action_timer = None

		repeat = getLastScriptRepeatCount()

		# ------------------------------------------------------------------ #
		# Double press → song-capture mode (or stop it if already recording)  #
		# ------------------------------------------------------------------ #
		if repeat >= 1:
			# A single-press action was queued but not yet executed — cancel it
			# so the double press does not also trigger a normal instant recording.

			if self._recorder.is_song_capture():
				# Song-capture is active: user manually ends the recording early.
				def _stop_song_capture():
					path = self._recorder.stop_song_capture()
					if path:
						wx.CallAfter(
							_notify,
							# Translators: Spoken when the user manually ends an in-progress song-capture recording (double-press Ctrl+Win+E while capturing); %s is the saved filename.
							_("Song recording stopped: %s") % os.path.basename(path),
						)
					else:
						# Translators: Fallback spoken when song-capture is stopped but no output path was returned (e.g. nothing was actually captured).
						wx.CallAfter(_notify, _("Song recording stopped"))
				threading.Thread(
					target=_stop_song_capture,
					daemon=True,
					name="FreeRadio-SongRecordingFinalize",
				).start()
				return

			if not self._player.has_media():
				# Translators: Spoken when the delayed single-press action fires and finds nothing is playing.
				ui.message(_("No station is playing"))
				return

			# Check whether the current station publishes ICY metadata.
			def _start_song_capture():
				from . import radioPlayer as _rp

				station = self._player.get_current_station()
				# Deliberately keyed off "media_kind" rather than the free-text
				# "tags" field: a real Radio Browser station can legitimately
				# carry "podcast"/"audiobook"/"jukebox" as a community-assigned
				# genre tag on an ordinary live stream (e.g. talk-radio mirrors
				# of podcast-hosting platforms like Zeno.fm or Qingting.fm) -
				# matching against "tags" used to make such a station wrongly
				# refuse song-capture recording. See
				# radioPlayer._is_seekable_media()'s docstring and
				# GlobalPlugin.script_addToFavorites() in __init__.py for the
				# same reasoning already applied elsewhere.
				media_kind = station.get("media_kind") if station else None
				is_podcast_or_audiobook = media_kind in ("podcast", "audiobook")
				is_jukebox = media_kind == "jukebox"

				if is_podcast_or_audiobook:
					# Translators: Spoken when double-pressing Ctrl+Win+E (song-capture) on a podcast/audiobook episode, which can't be recorded this way; points to the Ctrl+Win+V download command instead.
					wx.CallAfter(ui.message, _("Podcast or audiobook cannot be recorded. To download the episode or book, press Ctrl+Win+V."))
					return

				# Jukebox tracks are local files already on disk - there is
				# nothing to record, and unlike podcasts/audiobooks there is
				# no Ctrl+Win+V download alternative to point the user to
				# (script_addToFavorites already refuses jukebox tracks too).
				if is_jukebox:
					# Translators: Spoken when double-pressing Ctrl+Win+E (song-capture) on a jukebox track, which is already a local file.
					wx.CallAfter(ui.message, _("Jukebox tracks are already local files and cannot be recorded."))
					return

				# Try the fast in-memory title first; fall back to a live HTTP probe.
				icy = self._player.get_icy_title()
				if not icy:
					url = (
						getattr(self._player, "_current_url_resolved", None)
						or getattr(self._player, "_current_url", None)
					)
					if url:
						icy = _rp._read_icy_title_via_playlist(url)

				if not icy:
					# Station does not broadcast ICY metadata — inform the user and abort.
					wx.CallAfter(
						ui.message,
						# Translators: Spoken when trying to start song-capture recording on a station with no ICY track-title metadata, so there's no song boundary to record against.
						_("This station does not broadcast track metadata. Song recording is not available."),
					)
					return

				# Stop any plain instant recording that may already be running.
				if self._recorder.is_recording() and not self._recorder.is_song_capture():
					self._recorder.stop(self._player)

				try:
					self._recorder.start_song_capture(self._player, icy, timeshift_buffer=self._player.get_timeshift_buffer())
					wx.CallAfter(
						ui.message,
						# Translators: Spoken when song-capture recording starts; %s is the current ICY track title (artist/song) being captured.
						_("Song recording started: %s") % icy,
					)
				except Exception as exc:
					log.error("FreeRadio: song capture failed to start: %s", exc)
					# Translators: Generic fallback spoken if starting song-capture recording raises an unexpected exception.
					wx.CallAfter(ui.message, _("Could not start song recording"))

			threading.Thread(target=_start_song_capture, daemon=True).start()
			return

		# ------------------------------------------------------------------ #
		# Single press → instant recording (stop if active; start if not)     #
		# The action is delayed slightly so a quick double press can cancel it #
		# before it fires.                                                     #
		# ------------------------------------------------------------------ #
		def _do_single_press():
			self._record_action_timer = None

			# If song-capture is active, single press does nothing (double-press stops it)
			if self._recorder.is_song_capture():
				return

			station = self._player.get_current_station()
			# See the matching comment in _start_song_capture() above - keyed
			# off "media_kind" rather than "tags" for the same reason.
			media_kind = station.get("media_kind") if station else None
			is_podcast_or_audiobook = media_kind in ("podcast", "audiobook")
			is_jukebox = media_kind == "jukebox"

			# If a recording is already running, stop it (user may want to end it)
			if self._recorder.is_recording():
				def _stop_recording():
					path = self._recorder.stop(self._player)
					if path:
						# Translators: Spoken when the single-press gesture stops an in-progress plain instant recording; %s is the saved filename.
						wx.CallAfter(_notify, _("Recording stopped: %s") % os.path.basename(path))
					else:
						# Translators: Fallback spoken when a recording is stopped but no output path was returned.
						wx.CallAfter(_notify, _("Recording stopped"))
				threading.Thread(target=_stop_recording, daemon=True, name="FreeRadio-RecordingFinalize").start()
				return

			# No recording; if it's a podcast/audiobook, warn and abort
			if is_podcast_or_audiobook:
				# Translators: Same message as the song-capture path above, spoken here when single-pressing Ctrl+Win+E on a podcast/audiobook episode.
				wx.CallAfter(ui.message, _("Podcast or audiobook cannot be recorded. To download the episode or book, press Ctrl+Win+V."))
				return

			# No recording; a jukebox track is already a local file, so
			# there's nothing to record - warn and abort rather than
			# starting a pointless recording of a local file.
			if is_jukebox:
				# Translators: Same message as the song-capture path above, spoken here when single-pressing Ctrl+Win+E on a jukebox track.
				wx.CallAfter(ui.message, _("Jukebox tracks are already local files and cannot be recorded."))
				return

			if not self._player.has_media():
				# Translators: Spoken when the double-press (song-capture) gesture is used while nothing is playing.
				wx.CallAfter(ui.message, _("No station is playing"))
				return

			name = self._player.get_current_name()
			try:
				self._recorder.start(self._player, name, timeshift_buffer=self._player.get_timeshift_buffer())
				# Translators: Spoken when a plain instant recording starts (single-press Ctrl+Win+E); %s is the station name.
				wx.CallAfter(_notify, _("Recording started: %s") % name)
			except Exception as exc:
				log.error("FreeRadio: instant recording failed to start: %s", exc)
				# Translators: Generic fallback spoken if starting an instant recording raises an unexpected exception.
				wx.CallAfter(ui.message, _("Could not start recording"))

		# Delay single-press action by 350 ms so a second press can cancel it.
		self._record_action_timer = wx.CallLater(350, _do_single_press)

	@script(
		# Translators: Name of an NVDA command (Ctrl+Win+W); opens the configured recordings folder in File Explorer.
		description=_("Open FreeRadio recordings folder"),
		category=_("FreeRadio"),
		gesture="kb:control+windows+w",
	)
	def script_openRecordingsFolder(self, gesture):
		custom_dir = config.conf["freeradio"].get("recordings_dir", "").strip()
		if custom_dir and os.path.isabs(custom_dir):
			recordings_dir = custom_dir
		else:
			recordings_dir = os.path.join(os.path.expanduser("~"), "Documents", "FreeRadio Recordings")
		os.makedirs(recordings_dir, exist_ok=True)
		try:
			os.startfile(recordings_dir)
		except Exception as e:
			# Translators: Spoken when the Ctrl+Win+W shortcut can't open the recordings folder in Explorer; %s is the underlying error.
			ui.message(_("Could not open recordings folder: %s") % str(e))