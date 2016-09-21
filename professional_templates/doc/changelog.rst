.. _changelog:

Changelog
=========

`Version 0.5 (2016-06-10)`
----------------

- Added a setting to allow user to specify the ``Font-Family`` for the reports. Default font-family is configured in the company profile.

- Added a feature to automatically hide 'Taxes' column when there is not tax to charge

- Minor changes in the ``Iconography`` to be compatible with Windows Server Installations


`Version 0.4 (2016-05-24)`
----------------

- Added Parameter for user to adjust ``Font-size`` in each report header, body and footer

- Now fully compatible with the any version of ``wkhtmltopdf`` including the latest stable release: 0.12.3 (with patched qt)

- Removed the ``120 pixel`` height limit on Logo images. Now user can  use larger images

- Improved design to maximize space utilization

- Added Barcode images in Picking list and Delivery templates


`Version 0.3 (2016-03-26)`
----------------

- removed ``Required`` field feature in all Template Selection drop-down lists. This was to avoid some templates not getting 
  deleted when module is ``un-installed`` then ``re-installed`` and hence avoided seeing ``duplicate`` or ``triplicate`` templates 
  in the drop-down list.

- When ``Social Media IDs`` are not defined, the bar is no longer displaying hence the report looks neat.

- Further improvements done and known bugs fixed in all the templates.

- Added this Changelog to help clients to figure out whats new in the latest release.
