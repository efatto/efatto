#!/usr/bin/env bash
OE_USER=pi
su - $OE_USER -c "cd && git clone -b master --depth 1 git@gitlab.com:sergio-corato/simplerpos.git /home/'${OE_USER}'/odoo"
reboot