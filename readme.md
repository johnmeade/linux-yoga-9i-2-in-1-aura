# Feature Support

Most testing done on Fedora 41. I recommend using the latest stable Fedora, or a distro with a recent 6.14 kernel.

✅ Should work on kernel 6.12+, earlier verisons unknown:
* bluetooth
* wifi
* fingerprint reader
* ambient light sensor
* "basic" tablet mode switch (for disabling keyboard / touchpad in tablet mode)
  * only works when fully rotated flat
  * requires fully closing the laptop to re-enable keyboard / touchpad

✅ Working on 6.14 (and latest stable Fedora, on kernel 6.13, via driver backport), not working on 6.12 or earlier:
* touchscreen input
* pen/stylus - touch input
* pen/stylus - pressure
* pen/stylus - tilt

⚠️ Working after updating audio packages / configs (see next sections):
* internal microphone input
* headphone jack output

⚠️ Partially working
* "special" keys on keyboard
  * top star (with an S in it) maps to a standard "Favourites" key
  * the audio settings key on the right can be used / remapped out-of-the-box (keycode 149 "KEY_PROG2")
  * the "dial meter" key (top on the right) does not emit a keycode / event
  * several other keys emit keycode 240 "KEY_UNKNOWN" and may not be possible to use: "mode" key (Fn+F9), F11 alternate (Fn+F11), eyeball, hollow star
  * all other keys work as expected

❌ Not working:
* internal speaker output
  * may require kernel updates for support
  * may be related to ACPI powering the amplifier (?)
* accelerometer (for disabling keyboard / touchpad in "tent" mode, >180deg rotation)

❓ Untested:
* headphone jack mic input
* touchscreen support with kernel 6.13 on other distros
* kernel versions below 6.12


# Update Audio Packages / Config

Updating `sof firmware` and `Alsa UCM` configs should fix most of the audio issues (mic + headphone combo jack), but sadly this doesn't fix the internal speaker output.

These updates should be "safe", in the sense that they should simply be overwritten by future package updates, so forgetting about these edits shouldn't cause trouble in the future.

Download & install latest sof firmware, instructions:
https://github.com/thesofproject/sof-bin?tab=readme-ov-file#install-process-with-installsh---release-tarballs

Example:
```sh
wget https://github.com/thesofproject/sof-bin/releases/download/v2025.01/sof-bin-2025.01.tar.gz
tar xf sof-bin-2025.01.tar.gz
cd sof-bin-2025.01
sudo ./install.sh
```

Download & install latest Alsa UCM, instructions:
https://github.com/alsa-project/alsa-ucm-conf?tab=readme-ov-file#installation

Example:
```sh
# tested commit c3314b9ca29861d19164d2b3987745b7170dab06
cd ~/Downloads
curl -L -o alsa-ucm-conf.tar.gz https://github.com/alsa-project/alsa-ucm-conf/archive/refs/heads/master.tar.gz
sudo tar xvzf alsa-ucm-conf.tar.gz -C /usr/share/alsa --strip-components=1 --wildcards "*/ucm" "*/ucm2"
```

Reboot. The internal mic and headphone jack should be fixed! Internal speakers not working yet.

# Battery Life

![battery plot](https://github.com/johnmeade/linux-yoga-9i-2-in-1-aura/blob/main/yoga-9i-2-in-1-battery-plot.png?raw=true)
