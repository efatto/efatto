Professional Report Templates Documentation
===========================================
Installation
------------
NOTE: Before you proceed to install this module, please check the `Pre-Installation Requirements` section below.
This Module is a standard Odoo Module. Once you purchase it, please follow the following steps to install it:

- A download link will appear on the module description page.

- You need to extract the downloaded file into Odoo 'addons' directory where all other modules are kept.

- You then need to click on ``Updates Apps list`` for the new module to appear on the list of Apps.

- Then you click on ``Install`` and wait for it to finish

- After that you can go to configure the Logos, colors and your favorite templates as the default templates ...refer to Module ``Description`` for configuration



Configuration
-------------
Please refer to `Module Description` for illustrated steps on how to configure the default templates, colors and logos for your reports

Pre-Installation Requirements
---------------------------

- Download and install python module called ``num2words`` version ``0.5.3``. Download link:`https://github.com/savoirfairelinux/num2words`. We recommend that you download the source package and then      execute: `python setup.py install` while inside the package directory.

- Download and install ``wkhtmltopdf`` version ``0.12.1 (with patched qt)`` or higher. Version 0.12.3 (with patched qt) is recommended for excellent results


Compatibility
------------

- Fully Supports Odoo Version 8.0 standard installation



Frequently Asked Questions (FAQs)
===========================================

 - How do I print the reports in a different language?

   	Most of these report templates are usually sent to the customer via email or hard copy. It is important to print the report in a language of your customer.

	If you want your report to be printed in a different language other than the default English, you need to ensure that your customer/Partner Language settings is correct. The report will be translated to the language setting of the Customer/Partner. This language setting is found in the Customer/Vendor/Partner Form
 
	The module has been translated to `German`, `Italian`, `Spanish`, `Norwegian` and `French` so far....more Languages will be added soon. Please check on Module description for updates on which languages are available. 

	You can also purchase the module and request for translation to a language of your choice and it will be ready in less than 24 hours.



 - The `Header` is overlapping the `Body` content of the report?

	
	This is usually caused by the `Logo` or the `Company Address` being too large.

	This is not a big problem since in Odoo you can adjust the Paper Sizes to match the size of your logo or Address.

		- If this happens, login as admin to access the Extra `Technical Settings` 

		- Go to `Settings -> Technical -> Reports -> Paper Format` and open `European A4`

		- Adjust the `Top Margin` and `Header Spacing` until you get an optima size to match the size of your logo or address
 
