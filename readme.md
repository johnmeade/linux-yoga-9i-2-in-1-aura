All major functionality is working in recent versions of kernel & firmware, with some simple config updates.
Caveats:
* There is a full system freeze issue that can happen, which requires a reboot. It's mostly seen under high load or shortly after wake-up. It's pretty rare under light-to-medium load.
* Sometimes Bluetooth will enter an unusable buggy state on wake-up. Reboot fixes it, other solutions not explored yet.

I recommend using the latest stable Fedora as a starting point.

If your distro uses old packages / kernels / firmware, you may run into some of these issues:
* If Bluetooth doesn't work, follow the "Bluetooth Fix" section below (create a couple symlinks).
* If audio doesn't work, follow the Alsa UCM step in the "Troubleshooting Audio" section below (download some config files and reset alsa).

If you have any issues, you can report them here or on [this thread](https://forums.lenovo.com/t5/Other-Linux-Discussions/Linux-Support-Yoga-9i-2-in-1-Aura/m-p/5363703) on the Lenovo forums.

Feel free to open issues or PRs if you have something to ask or share!

# General Stability

There is a power management bug that can sometimes cause the CPU cores to get "stuck" in their low-power state (400MHz) for about 1 minute when waking from suspend. This rarely happens to me, and I've never seen this issue persist longer than 1 minute, but [reports](https://www.phoronix.com/review/lunarlake-xe2-windows-linux-2025) from similar models (like the X1 Carbon Aura) suggest it's possible they remain stuck unless you switch to the "Performance" power mode (ie in Gnome settings).

There is also a rare full system freeze issue that requires reboot, perhaps most likely to occur just after wakeup, but the cause of this is unknown. Perhaps it's related to the issue above.

A similar rare bug is a full system freeze followed by a forced reboot shortly after. I've experienced this while playing games or sometimes with other high-load applications. I'm not sure of the cause for this one either, perhaps the CPU/GPU load is related.

System freezes / crashes seem very rare with light / medium workloads (eg a browser, vscode, slack, spotify, etc).

# Feature Support

Most testing below was done on Fedora 41 & 42.

✅ Should work on kernel 6.12+, earlier verisons unknown:
* wifi
* fingerprint reader
* ambient light sensor
* disabling keyboard / touchpad in tablet mode
  * only works out-of-the-box when fully rotated flat
  * older configurations may require fully closing the laptop to re-enable keyboard / touchpad
  * see "ISH Workaround" below for full functionality

✅ Working on 6.14 (and some 6.13, via driver backport, eg Fedora), not working on 6.12 or earlier:
* touchscreen input
* pen/stylus - touch input, pressure, tilt, side buttons

✅ Working but may require manual fixes:
* audio (some old `linux-firmware` packages may not have correct configuration, see "Troubleshooting Audio" section below if you have an issue)
  * internal speaker output
  * internal microphone input
  * headphone jack output
* bluetooth
  * some old `linux-firmware` packages may have misconfigured bluetooth firmware for some Lunar Lake chipsets, see "Bluetooth Fix" below if you have an issue.
* suspend
  * some distros may wake immediately due to touchpad wake events, easy to fix, see "Troubleshooting Suspend" section below
* the copilot key is recognised as a bizzare key macro, but can be remapped (for example, to Right Ctrl) using the Input Remapper software (see "Key Remapping" below) on 6.14 (remapping untested on 6.13 or earlier).
* gyro / accelerometer  (auto-rotate, disabling keyboard/mouse, "tent" mode)
  * firmware files must be manually copied from a Windows installation or ISH driver, see "ISH Workaround" below

✅ Working on latest Fedora 43 (results will vary across distributions / kernels)
* most "special" keys on keyboard
  * the power mode key (top right below "delete") works as expected in Fedora -- this may be distro / desktop dependent
  * the audio settings key, eyeball key, and hollow star key on the right should be usable out-of-the-box on recent distros (they are mapped to generic launcher keys in Fedora 43)

⚠️ Partially working
* some "special" keys on keyboard may emit keycode 240 "KEY_UNKNOWN" (Fn+F9 and Fn+F11 do this on Fedora 43)
  * these can only partially be used (see "Key Remapping" below), and they likely overlap with each other, so you cannot map different functions to each special key independently.

❗ Other issues:
* When waking from a long suspend, sometimes there is temporary lag for around 1 minute
* There is a full system freeze issue that can happen, typically on wake-up or under high CPU+GPU load, which requires a hard reboot.
* Sometimes bluetooth stops working when waking up

❓ Untested:
* headphone jack mic input (probably fine?)
* touchscreen support with kernel 6.13 on other distros
* kernel versions below 6.12


# ISH Workaround (auto-rotate, disabling keyboard/mouse, "tent" mode)

Credit: https://dnsense.pub/posts/9-book5-sensor-hub/ and DeltaWhy for reporting

The Intel "Integrated Sensor Hub" uses proprietary firmware that is not upstreamed in the Linux kernel. However, the file distributed to Windows installations works as-is with no modifications, and can just be copy-pasted into Linux.

Warning: Assume this firmware file isn't legal to redistribute. Only copy it from your own installation and don't share it. I think upstreaming is possible but may require Lenovo and/or Intel's sign-off.

**Step 1: Obtain the firmware file**

If you still have a Windows partition, boot into Windows, and copy the firmware file out from `C:\Windows\System32\DriverStore\FileRepository\ishheciextensiontemplate.inf_amd64_[RANDOM_STRING]\FwImage\0003\ishS_MEU_aligned.bin` (or similar), and skip to Step 2.

If you deleted your Windows partition, you have to extract the firmware from the driver distributed by Lenovo.

Download the `Intel Integrated Sensor Hub Driver for Windows 11 (64-bit) - Yoga 9 2-in-1 14ILL10`, from [here](https://pcsupport.lenovo.com/ca/en/products/laptops-and-netbooks/yoga-series/yoga-9-2-in-1-14ill10/downloads/ds572874-intel-integrated-sensor-hub-driver-for-windows-11-64-bit-yoga-9-2-in-1-14ill10?category=Motherboard%20Devices%20%28Backplanes,%20core%20chipset,%20onboard%20video,%20PCIe%20switches%29).

You can try to use `wine` directly, but you may have `.NET` issues, in which case you can just use `bottles`.

Eg for Fedora: `sudo dnf install bottles`

Create a bottle, run the exe, select "extract only", and then grab the firmware file from `drive_c`! For flatpak Bottles it should be:

`~/.local/share/bottles/bottles/ish-driver/drive_c/DRIVERS/IntegratedSensorHub/20252309.10342242/Source/IshHeciExtensionTemplate/x64/FWImage/0003/ishS_MEU_aligned.bin`

This dir may change depending on install method, eg it might be at

`~/.var/app/com.usebottles.bottles/data/bottles/...`


**Step 2: Install the firmware file**

```sh
# backup any existing files in here, in my case just one file
sudo mv /lib/firmware/intel/ish/{,__BACKUP__}ish_lnlm.bin.xz

# replace firmware
sudo mv ishS_MEU_aligned.bin /lib/firmware/intel/ish/ish_lnlm.bin

# update initial ramdisk
sudo dracut --force  # Fedora
sudo update-initramfs -u  # Ubuntu
# etc

reboot
```

The result should be a working gyro / accelerometer, including disabling the keyboard and auto-rotating the screen!

To confirm you've loaded the new file, you can check `sudo dmesg | grep ish`, for eg:

```
[    2.946244] intel_ish_ipc 0000:00:12.0: ISH loader: load firmware: intel/ish/ish_lnlm.bin
[    2.970930] intel_ish_ipc 0000:00:12.0: ISH loader: firmware loaded. size:526848
[    2.970933] intel_ish_ipc 0000:00:12.0: ISH loader: FW base version: 5.8.0.7720
[    2.970934] intel_ish_ipc 0000:00:12.0: ISH loader: FW project version: 1.0.6.12644
```


# Bluetooth Fix

If you have bluetooth issues, run this:

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

Reboot. It might also require updating initial ramdisk:

```sh
sudo dracut --force  # Fedora
sudo update-initramfs -u  # Ubuntu
# etc
```

before reboot.
If that doesn't work, update firmware with upstream and retry,

```sh
mkdir bt-fw-backup
sudo mv /lib/firmware/intel/ibt-0190-* bt-fw-backup
git clone https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
sudo cp linux-firmware/intel/ibt-0190-* /lib/firmware/intel/
```


# Key Remapping

NOTE: if your distro uses Python 3.14, version InputRemapper v2.2.0 or higher is required.

The [Input Remapper](https://github.com/sezanzeb/input-remapper) app can convert the "unknown" key events, pen buttons, the co-pilot key, etc, into other key events / macros. Limitations:

* Depending on your distro / kernel / firmware / etc, some special keys will do the same thing, and can't be remapped independently.
* With the exception of the copilot key, the special key events emitted by the Lenovo drivers do not have a "held" state (they instantly trigger a "key up" event after the initial "key down"), so you can't exactly simulate holding a modifier key like `Ctrl` (but there is a workaround below).

After installing, click the "Ideapad Extra Buttons" section, add a preset, click "record", record the key stroke, and then enter a macro in the field to the right.

### Example 1

Hold down Ctrl for 1 second when a key is pressed. This gives you a moment to use a "special" key as a normal modifier, since most of them do not have a held state (except the copilot key)

```js
key_down(KEY_LEFTCTRL).wait(1000).key_up(KEY_LEFTCTRL)
```

### Example 2

Remap the unknown keys to `XF86Launch1` so it can then be bound as usual from your desktop environment settings,

```js
key(XF86Launch1)
```

Now, this key should work as a generic extra key that you can bind commands to (confirmed to work in Gnome).

### Example 3

You can remap buttons on the stylus / pen too. To do this, select the "Wacom [...] Pen" device, add an input, and click record. If the pen is far from the screen, the pen buttons will not emit any events. Make sure the pen is hovering above the screen, controlling the mouse, before pressing the button you want to remap while recording. The remapper will capture several events related to tilt and movement, so you have to click "advanced" and manually remove those entries. You should end up with a single input event named "Button STYLUS" or similar. Now you can remap this to whatever you want, for example Ctrl+Space,

```js
modify(KEY_LEFTCTRL, key(KEY_SPACE))
```

(This can be useful for apps that don't handle certain events like "Button STYLUS" natively.)

### Suggested setup

* copilot key remapped to `KEY_RIGHTCTRL` (works as a normal key, ie with distinct keyup / keydown events)
* unknown keys remapped to `XF86Launch1`, `XF86Launch3`, etc as generic app launchers
  * which keys can be mapped independently may be distro / kernel dependent
  * note that the "audio settings" key may already be mapped to `XF86Launch2`
* pen buttons remapped as needed for your drawing software


# Battery Life


Using "Balanced" power mode (Gnome 47 / Fedora 41)
![battery plot](yoga-9i-2-in-1-battery-plot.png)

Suspend test (Fedora 42, kernel 6.14.6)
![suspend battery plot](yoga-9i-2-in-1-suspend-battery-plot.png)


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
Description=Disable wakeup for ELAN touchpad
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

This is likely only applicable to distros that use very old Linux packages.

If you have a version of linux firmware newer than March 14, 2025, you should skip this and try the Alsa UCM and sof firmware steps below.

Updating from an old linux firmware version is likely to help fix audio issues.

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
sudo systemctl stop alsa-state
sudo rm /var/lib/alsa/asound.state
sudo systemctl start alsa-state
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

## Audio on Ubuntu 24.04

First follow the previous steps to install latest `alsa-ucm` and `sof` firmware and then modify the following file:

```nano /usr/share/alsa/ucm2/sof-soundwire/sof-soundwire.conf```
and replace in the first line `Syntax 7` with `Syntax 6`

This is necessary because the alsaucm binaries in Ubuntu 24.04 don't support the latest syntax.
You can confirm that it is working by running `alsaucm listcards`, it should produce the following result:
```sh
  0: hw:0
    LENOVO-83LC-Yoga92_in_114ILL10-LNVNB161216
```

If you still encounter problems please run `alsa-info` and compare your output to the following one:

http://alsa-project.org/db/?f=00aaa2b0024b2e1a9641d978f526ff44576577b6


# Misc

(April 24, 2025) There is currently a strange bug that crashes Gnome entirely, sending you back to the login screen. It seems to happen when:
* you are in tablet mode with the on-screen keyboard open
* you click a button on certain GTK dialog boxes, like a "save" dialog box

For example, saving a file within RNote with the on-screen keyboard open will likely cause a crash (your file should be saved correctly though).

This is a complex interaction between Mutter/Wayland and Gnome, *possibly* related to GTK or other apps.
