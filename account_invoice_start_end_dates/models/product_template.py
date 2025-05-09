# Copyright 2013-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    must_have_dates = fields.Boolean(
        string="Must Have Start/End Dates",
        help="If this option is active, the user will have to enter "
        "a Start Date and an End Date on the invoice lines that have "
        "this product.",
    )
