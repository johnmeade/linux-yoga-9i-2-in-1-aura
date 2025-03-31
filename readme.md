All major functionality is now working in recent versions of kernel & firmware.
Distros that favor older versions of these for general stability may take a few more months to receieve the necessary changes.
I recommend using the latest stable Fedora as a starting point.
For Fedora, simply install all system updates, reboot, check if Bluetooth works, and follow the "Bluetooth Fix" section below if needed.

# Feature Support

Most testing below was done on Fedora 41.

✅ Should work on kernel 6.12+, earlier verisons unknown:
* wifi
* fingerprint reader
* ambient light sensor
* "basic" tablet mode switch (for disabling keyboard / touchpad in tablet mode)
  * only works when fully rotated flat
  * requires fully closing the laptop to re-enable keyboard / touchpad
  * see "Tablet-mode Quirk" section below

✅ Working on 6.14 (and some 6.13, via driver backport, eg Fedora), not working on 6.12 or earlier:
* touchscreen input
* pen/stylus - touch input, pressure, tilt, side buttons

✅ Working with newer kernel / firmware versions (or see "Troubleshooting Audio" section below):
* internal speaker output
* internal microphone input
* headphone jack output

✅ Working but may require manual fixes:
* bluetooth
  * firmware is temporarily misconfigured upstream for some Lunar Lake chipsets, see "Bluetooth Fix" below if you have an issue.
* suspend
  * some distros may wake immediately due to trackpad wake events, easy to fix, see "Troubleshooting Suspend" section below

⚠️ Partially working
* "special" keys on keyboard
  * top star (with an S in it) maps to a standard "Favourites" key
  * the power mode key (top right below "delete") works as expected in Fedora -- this may be distro / desktop dependent
  * the audio settings key on the right can be used / remapped out-of-the-box (keycode 149 "KEY_PROG2")
  * several other keys emit keycode 240 "KEY_UNKNOWN" ("mode" key Fn+F9, Fn+F11, and the eyeball & hollow star on the bottom right)
    * these can only partially be used, see "Unknown Key Remapping" below:
  * all other keys work as expected

❌ Not working:
* accelerometer (for disabling keyboard / touchpad in "tent" mode, >180deg rotation)
  * see "Tablet-mode Quirk" section below

❗ Other issues:
* When waking from a long suspend, sometimes there is temporary lag for around 1 minute
* There seems to be a very rare full system freeze issue that can happen, which requires a hard reboot.

❓ Untested:
* headphone jack mic input (probably fine?)
* touchscreen support with kernel 6.13 on other distros
* kernel versions below 6.12


# Bluetooth Fix

As of March 15 2025, Fedora stable firmware breaks bluetooth. Other distros running newer versions of `linux-firmware` will probably have the same issue. Run this:

```sh
sudo dmesg | grep -i bluetooth
```

If you have a line like this:

```
[    3.646023] Bluetooth: hci0: Failed to load Intel firmware file intel/ibt-0190-0291-pci.sfi (-2)
```

Then follow the steps below.

The issue can be fixed by symlinking some firmware files:

```sh
sudo ln -s /lib/firmware/intel/ibt-0190-0291.sfi /lib/firmware/intel/ibt-0190-0291-pci.sfi
sudo ln -s /lib/firmware/intel/ibt-0190-0291.ddc /lib/firmware/intel/ibt-0190-0291-pci.ddc
```

Reboot. It might also require:

```sh
sudo dracut --force
# (note: your distro might use `initramfs`)
```

before reboot.
If that doesn't work, update firmware with upstream and retry,

```sh
mkdir bt-fw-backup
sudo mv /lib/firmware/intel/ibt-0190-* bt-fw-backup
git clone https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
sudo cp linux-firmware/intel/ibt-0190-* /lib/firmware/intel/
```


# Unknown Key Remapping

The [Input Remapper](https://github.com/sezanzeb/input-remapper) app can convert the "unknown" key events into other key events / macros. Limitations:

* All 4 "unknown" keys will do the same thing, they can't be remapped independently
* The special key events emitted by the Lenovo drivers do not have a "held" state (they instantly trigger a "key up" event after the initial "key down"), so you can't exactly simulate holding a modifier key like `Ctrl` (but there is a workaround below).

After installing, click the "Ideapad Extra Buttons" section, add a preset, click "record", record the key stroke, and then enter a macro in the field to the right.

### Example 1

Hold down Ctrl for 1 second when an unknown key is pressed -- this gives you a moment to use it as a normal modifier,

```js
key_down(KEY_LEFTCTRL).wait(1000).key_up(KEY_LEFTCTRL)
```

### Example 2

Remap the unknown keys to `XF86Launch1` so it can then be bound as usual from your desktop environment settings,

```js
key(XF86Launch1)
```

Now, this key should work as a generic extra key that you can bind commands to (confirmed to work in Gnome). There are many other random key names that you can bind if this doesn't work.

Or of course, or you just can map that one key to a macro / sequence of keys, and use that same sequence as a key shortcut in your desktop settings.


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


Using "Balanced" power mode (Gnome 47 / Fedora 41)
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

⚠️ As of March 14, 2025, bluetooth may be broken on some newer firmware releases.
See the "Bluetooth Fix" section for a fix.

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
