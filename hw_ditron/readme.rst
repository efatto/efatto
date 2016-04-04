.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg

==============================================
Driver for Ditron Fiscal Printer
==============================================

This module send a file to a shared folder to be monitored from SoECRCom driver
of WinEcrCom module on Windows.


Contributors
------------

* Sergio Corato <sergio.corato@gmail.com>
=========================================


Configuration
-------------

This module has to be installed in a machine prepared with Debian 8.x server in
a VirtualBox (or equivalent) using script:
    hw_ditron/tools/install.sh
launched as root (this module is installed automatically with this script).
This script create a PosBox installation of Odoo.
After creation, to work it need to:
    - add Guest Additions to VirtualBox;
    - share the folder /home/pi/share with the parent os (usually Windows)
    - configure WinEcrCom with the same shared folder

Preferably configure Debian machine in VirtualBox with static IP, taking an IP
far from the ones normally used, likes:
auto eth0
iface eth0 inet static
             address 192.168.0.189
             netmask 255.255.255.0
             gateway 192.168.0.1
#to verify
             #dns-search somedomain.org
             #dns-nameservers 195.238.2.21 195.238.2.22
             #broadcast 192.168.0.0
This IP will be put in as 'proxy' in Odoo POS configuration.

To update the Simplerpos, only do (there isn't a db):
    su - pi
    cd odoo
    git pull -u
    exit
    reboot

TODO:
    - print receipt if queue is full (now they are saved with another name)

Maintainer
----------

.. image:: https://www.simplerp.it/website_logo.png
   
:alt: SimplERP Srl
   :target: http://simplerp.it

This module is maintained by SimplERP Srl.

SimplERP is the professional edition of LibrERP.it project, which promotes a customized Odoo with additional features for Italian usage.

To contribute to this module, please visit http://librerp.it.