# Copyright 2012-2017 Camptocamp SA
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResPartnerPaymentActionType(models.Model):
    _name = "res.partner.payment.action.type"
    _description = "Partner Payment Action Types"
    _order = "sequence, id"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    partner_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="payment_next_action_type",
        string="Partners",
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)


class ResPartner(models.Model):
    """Add a settings on the credit control policy to use on the partners,
    and links to the credit control lines.
    """

    _inherit = "res.partner"

    credit_policy_id = fields.Many2one(
        comodel_name="credit.control.policy",
        string="Credit Control Policy",
        help="The Credit Control Policy used for this "
        "partner. This setting can be forced on the "
        "invoice. If nothing is defined, it will use "
        "the company setting.",
    )
    credit_control_count = fields.Integer(
        compute="_compute_credit_control_count", string="# of Credit Control Lines"
    )
    payment_responsible_id = fields.Many2one(
        comodel_name="res.users",
        ondelete="set null",
        string="Follow-up Responsible",
        help="Optionally you can assign a user to this field, "
        "which will make him responsible for the action.",
        tracking=True,
    )
    payment_note = fields.Text(
        string="Customer Payment Promise",
        help="Payment Note",
        tracking=True,
    )
    payment_next_action_type = fields.Many2one(
        comodel_name="res.partner.payment.action.type",
        string="Next Action Type",
        tracking=True,
    )
    payment_next_action = fields.Text(
        string="Next Action",
        help="This is the next action to be taken.",
        tracking=True,
    )
    payment_next_action_date = fields.Date(
        string="Next Action Date",
        help="This is when the manual follow-up is needed.",
        tracking=True,
    )
    manual_followup = fields.Boolean()
    credit_control_analysis_ids = fields.One2many(
        "credit.control.analysis",
        "partner_id",
        string="Credit Control Levels",
        groups="account_credit_control.group_account_credit_control_info",
    )

    def _compute_credit_control_count(self):
        partners = self.filtered(lambda x: not x.parent_id)
        fetch_data = self.env["credit.control.line"].read_group(
            domain=[("partner_id", "in", partners.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )
        result = {
            data["partner_id"][0]: data["partner_id_count"] for data in fetch_data
        }
        for partner in self:
            partner.credit_control_count = result.get(partner.id, 0)

    @api.constrains("credit_policy_id", "property_account_receivable_id")
    def _check_credit_policy(self):
        """Ensure that policy on partner are limited to the account policy"""
        # sudo needed for those w/o permission that duplicate records
        for partner in self:
            if (
                not partner.property_account_receivable_id
                or not partner.sudo().credit_policy_id
            ):
                continue
            account = partner.property_account_receivable_id
            policy = partner.sudo().credit_policy_id

            try:
                policy.check_policy_against_account(account)
            except UserError as err:
                # constrains should raise ValidationError exceptions
                raise ValidationError(err) from err
