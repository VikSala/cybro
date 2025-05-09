# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        category_posted = cls.env["product.public.category"].create(
            {"name": "Category Test Posted", "sequence": 1}
        )
        cls.env["product.public.category"].create(
            {"name": "Category Test Not Posted", "sequence": 2}
        )
        cls.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "public_categ_ids": [category_posted.id],
            }
        )
        cls.env.ref("website_sale.products_categories").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_hide_empty_category", login="admin")
