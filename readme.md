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

✅ Working with newer kernel / firmware versions (or see "Troubleshooting Audio" section below):
* internal speaker output
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
* accelerometer (for disabling keyboard / touchpad in "tent" mode, >180deg rotation)

❓ Untested:
* headphone jack mic input (probably fine?)
* touchscreen support with kernel 6.13 on other distros
* kernel versions below 6.12


# Battery Life

![battery plot](https://github.com/johnmeade/linux-yoga-9i-2-in-1-aura/blob/main/yoga-9i-2-in-1-battery-plot.png?raw=true)


# Troubleshooting Audio

If you want to try fixing audio on outdated systems, you may try these steps. This is not an exhaustive list.

## Update Linux Firmware

If you can install the latest firmware, this is likely to fix some or all issues:

https://gitlab.com/kernel-firmware/linux-firmware

Your distro may have a mechanism to install newer testing versions.

## Update Audio Packages / Config

Updating `sof firmware` and/or `Alsa UCM` configs may fix audio issues.

### Step 1

First, try downloading & installing the latest Alsa UCM, instructions:
https://github.com/alsa-project/alsa-ucm-conf?tab=readme-ov-file#installation

Example:
```sh
# tested commit c3314b9ca29861d19164d2b3987745b7170dab06
cd ~/Downloads
curl -L -o alsa-ucm-conf.tar.gz https://github.com/alsa-project/alsa-ucm-conf/archive/refs/heads/master.tar.gz
sudo tar xvzf alsa-ucm-conf.tar.gz -C /usr/share/alsa --strip-components=1 --wildcards "*/ucm" "*/ucm2"

# ensure config is re-generated
systemctl stop alsa-state
rm /var/lib/alsa/asound.state
systemctl start alsa-state
```

Reboot and check if any sound issues have been resolved.

### Step 2

Next you can try downloading & installing the latest `sof` firmware, instructions:
https://github.com/thesofproject/sof-bin?tab=readme-ov-file#install-process-with-installsh---release-tarballs

Example:
```sh
wget https://github.com/thesofproject/sof-bin/releases/download/v2025.01/sof-bin-2025.01.tar.gz
tar xf sof-bin-2025.01.tar.gz
cd sof-bin-2025.01
sudo ./install.sh
```

Reboot and check if any sound issues have been resolved.
