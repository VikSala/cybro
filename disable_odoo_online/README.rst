========================
Remove odoo.com Bindings
========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:bd671a096d54b77df4e92d655fc181b362e41f3d713889cbd5017d7cd7362ad6
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fserver--brand-lightgray.png?logo=github
    :target: https://github.com/OCA/server-brand/tree/18.0/disable_odoo_online
    :alt: OCA/server-brand
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/server-brand-18-0/server-brand-18-0-disable_odoo_online
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/server-brand&target_branch=18.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module deactivates all bindings to odoo.com that come with the
standard code:

- update notifier code is deactivated and the function is overwritten.
  It's deactivated only in community version, because `it's not
  legal <https://www.odoo.com/documentation/user/12.0/legal/terms/enterprise.html#customer-obligations>`__
  to deactivate notifier code in odoo enterprise
- apps and updates menu items in settings are hidden inside Technical
  Parameters
- documentation, support and odoo.com account are removed from user menu

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-brand/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-brand/issues/new?body=module:%20disable_odoo_online%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Therp BV
* GRAP

Contributors
------------

- Holger Brunn <hbrunn@therp.nl>
- Stefan Rijnhart <stefan@opener.am>
- Sylvain LE GAL (https://twitter.com/legalsylvain)
- Hieu, Vo Minh Bao <hieu.vmb@komit-consulting.com>
- Lorenzo Battistini <https://github.com/eLBati>
- Dennis Sluijk <d.sluijk@onestein.nl>
- Dhara Solanki <dhara.solanki@initos.com> (http://www.initos.com)
- Vincent Hatakeyama <vincent.hatakeyama@xcg-consulting.fr>

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/server-brand <https://github.com/OCA/server-brand/tree/18.0/disable_odoo_online>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
