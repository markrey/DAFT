#!/bin/bash
#
# Copyright (c) 2016 Intel, Inc.
# Author Simo Kuusela <simo.kuusela@intel.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

set_up_overlay() {
  mkdir /ramdisk/upper
  mkdir /ramdisk/work
  mount -t overlay -o lowerdir=/_var,upperdir=/ramdisk/upper,workdir=/ramdisk/work overlay /var
}

set_up_gpio() {
  echo 60 > /sys/class/gpio/export
  echo out > /sys/class/gpio/gpio60/direction
  echo 0 > /sys/class/gpio/gpio60/value
}

set_up_system() {
  touch /var/lib/misc/dnsmasq.leases
  systemctl restart dnsmasq
  systemctl restart ssh
  chmod 777 /var/run/screen
  iptables-restore < /etc/iptables.rules
  dmesg -n 1
}

set_up_overlay
set_up_gpio
set_up_system
