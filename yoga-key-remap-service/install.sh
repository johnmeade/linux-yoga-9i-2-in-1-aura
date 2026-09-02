#!/usr/bin/env bash
# Installs the combined Yoga key remap daemon as a systemd --user service.
set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

needs_relogin=0
if ! groups "$USER" | grep -qw input; then
    echo "adding $USER to the 'input' group (needed to read the keyboard devices without sudo)"
    sudo usermod -aG input "$USER"
    needs_relogin=1
fi

mkdir -p ~/.local/bin
cp "$dir/yoga_key_remap.py" ~/.local/bin/yoga-key-remap-service
chmod +x ~/.local/bin/yoga-key-remap-service

mkdir -p ~/.config/systemd/user
cp "$dir/yoga-key-remap.service" ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable yoga-key-remap.service

if [ "$needs_relogin" -eq 1 ]; then
    echo
    echo "Group membership only takes effect after logging out and back in (or a reboot)."
    echo "After that, start the service with:"
    echo "  systemctl --user start yoga-key-remap.service"
else
    systemctl --user restart yoga-key-remap.service
    echo "yoga-key-remap.service started. Check status with:"
    echo "  systemctl --user status yoga-key-remap.service"
fi
