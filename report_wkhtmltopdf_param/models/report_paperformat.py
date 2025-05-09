# Copyright 2017 Avoin.Systems
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Paper(models.Model):
    _inherit = "report.paperformat"

    custom_params = fields.One2many(
        "report.paperformat.parameter",
        "paperformat_id",
        "Custom Parameters",
        help="Custom Parameters passed forward as wkhtmltopdf command arguments",
    )

    @api.constrains("custom_params")
    def _check_recursion_custom_params(self):
        for paperformat in self:
            sample_html = """
                <!DOCTYPE html>
                <html style="height: 0;">
                    <body>
                        <div>
                        <span itemprop="name">Hello World!</span>
                        </div>
                    </body>
                </html>
            """
            report = self.env["ir.actions.report"].new(
                {"paperformat_id": paperformat.id}
            )
            content = report._run_wkhtmltopdf([sample_html])
            if not content:
                raise ValidationError(
                    self.env._("Failed to create a PDF using the provided parameters.")
                )
