# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website sale order type",
    "summary": "This module allows sale_order_type to work with website_sale.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "maintainers": ["pilarvargas-tecnativa"],
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["website_sale", "sale_order_type"],
    "assets": {
        "web.assets_tests": [
            "/website_sale_order_type/static/tests/tours/website_sale_order_type_tour.esm.js"
        ]
    },
    "auto_install": True,
}
