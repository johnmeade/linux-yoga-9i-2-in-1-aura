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
  * see "Tablet-mode Quirk" section below

✅ Working on 6.14 (and some 6.13, via driver backport, eg Fedora), not working on 6.12 or earlier:
* touchscreen input
* pen/stylus - touch input
* pen/stylus - pressure
* pen/stylus - tilt

✅ Working with newer kernel / firmware versions (or see "Troubleshooting Audio" section below):
* internal speaker output
  * ⚠️ On Fedora 41, this currently requires the latest [testing](https://bodhi.fedoraproject.org/updates/FEDORA-2025-7f56eb37a0) package for linux firmware, which should be stable by April 2025. This specific linked advisory **breaks bluetooth** but hopefully this will be fixed soon.
* internal microphone input
* headphone jack output

✅ Working but may require manual fixes:
* suspend
  * some distros may wake immediately due to trackpad wake events, easy to fix, see "Troubleshooting Suspend" section below

⚠️ Partially working
* "special" keys on keyboard
  * top star (with an S in it) maps to a standard "Favourites" key
  * the audio settings key on the right can be used / remapped out-of-the-box (keycode 149 "KEY_PROG2")
  * the "dial meter" key (top on the right) does not emit a keycode / event
  * several other keys emit keycode 240 "KEY_UNKNOWN" and may not be possible to use: "mode" key (Fn+F9), F11 alternate (Fn+F11), eyeball, hollow star
  * all other keys work as expected

❌ Not working:
* accelerometer (for disabling keyboard / touchpad in "tent" mode, >180deg rotation)
  * see "Tablet-mode Quirk" section below

❓ Untested:
* headphone jack mic input (probably fine?)
* touchscreen support with kernel 6.13 on other distros
* kernel versions below 6.12


# Wakeup Slowdown Quirk

When the laptop has been in suspend for a long time, it may be a bit slow / laggy for 30 sec - 1 min after waking up. So far, I've never needed to reboot to fix this. Perhaps it will be addressed in future linux updates.


# Tablet-mode Quirk

The accelerometer is used to disable the keyboard / trackpad when rotating the screen into "tent" mode.
But since the accelerometer is not detected, this trigger is not going to work.
Luckily, there is another trigger for when the laptop is in "tablet" mode, fully rotated, which does work to disable the keyboard/trackpad.
However, it doesn't enable input when retruning the laptop to tent/laptop modes, so you have to fully close the laptop (triggering suspend as a side effect) to enable input again.
So, to use tent mode with key input disabled, you just have to enter tablet mode first.

### Workaround

The working sensors are magnetic, and can be triggered with the pen/stylus.
This can be decently consistent if you play with it for a while, but you'll probably trigger the "suspend" trigger while trying and your laptop will go to sleep.

* Disabling keyboard / trackpad
  * hold the Lenovo Pen with pointy end facing to the right (towards the Enter/Backspace key), and with the "Lenovo" logo facing **up**
  * tap the "eraser" end just to the left of the laptop, with a shallow angle, so the side of the pen touches the laptop between tilde/backtick and Tab
* Enabling keyboard / trackpad
  * hold the Lenovo Pen with pointy end facing to the right (towards the Enter/Backspace key), and with the "Lenovo" logo facing **down**
  * tap the "eraser" end just to the left of the laptop, with a shallow angle, so the side of the pen touches the laptop between tilde/backtick and Tab


# Battery Life

![battery plot](https://github.com/johnmeade/linux-yoga-9i-2-in-1-aura/blob/main/yoga-9i-2-in-1-battery-plot.png?raw=true)


# Troubleshooting Suspend

Some distros may immediately wake from suspend. One cause is erroneous wake signals from the touchpad.

If you suspect you have this issue, try suspending via your desktop environment or systemctl suspend, and wait a few seconds. If suspend fails / your login screen pops back up without any input, then run this:

```sh
sudo cat /sys/kernel/debug/wakeup_sources
```

and see if there is a "ELAN" device with a bunch of numbers. For example, the problem device may look like `i2c-ELAN06FA:00`. To check if it's the source  of your problem, run

```sh
echo "disabled" | sudo tee /sys/bus/i2c/devices/i2c-ELAN06FA:00/power/wakeup
```

and try suspending again. If your laptop suspends properly, then you just need to run this every boot to fix the issue permanently.

For systemd (Ubuntu, Fedora, many others), you can use a service file to do this:

```sh
sudo nano /etc/systemd/system/disable-elan-wakeup.service
```

add these lines:

```ini
[Unit]
Description=Disable wakeup for ELAN trackpad
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo "disabled" > /sys/bus/i2c/devices/i2c-ELAN06FA:00/power/wakeup'
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
```

then enable the service

```sh
sudo systemctl daemon-reload
sudo systemctl enable disable-elan-wakeup.service
sudo systemctl start disable-elan-wakeup.service
```

# Troubleshooting Audio

If you want to try fixing audio on outdated systems, you may try these steps. This is not an exhaustive list.

## Update Linux Firmware

⚠️ As of March 14, 2025, bluetooth may be broken on some newer firmware releases. Hopefully this will be fixed soon.

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
