# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError


class BaseCommentTemplate(models.Model):
    """Comment templates printed on reports"""

    _name = "base.comment.template"
    _description = "Comments Template"
    _order = "sequence,id"

    active = fields.Boolean(default=True)
    position = fields.Selection(
        string="Position on document",
        selection=[("before_lines", "Top"), ("after_lines", "Bottom")],
        required=True,
        default="before_lines",
        help="This field allows to select the position of the comment on reports.",
    )
    name = fields.Char(
        translate=True,
        required=True,
        help="Name/description of this comment template",
    )
    text = fields.Html(
        string="Template",
        translate=True,
        required=True,
        sanitize=False,
        help="This is the text template that will be inserted into reports.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        ondelete="cascade",
        index=True,
        help="If set, the comment template will be available only for the selected "
        "company.",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="base_comment_template_res_partner_rel",
        column1="base_comment_template_id",
        column2="res_partner_id",
        string="Partner",
        help="If set, the comment template will be available only for the selected "
        "partner.",
    )
    models = fields.Text(required=True)
    model_ids = fields.Many2many(
        comodel_name="ir.model",
        compute="_compute_model_ids",
        compute_sudo=True,
        string="IR Model",
        help="This comment template will be available on this models. "
        "You can see here only models allowed to set the coment template.",
        search="_search_model_ids",
    )
    domain = fields.Char(
        string="Filter Domain",
        required=True,
        default="[]",
        help="This comment template will be available only for objects "
        "that satisfy the condition",
    )
    sequence = fields.Integer(
        required=True, default=10, help="The smaller number = The higher priority"
    )
    engine = fields.Selection(
        selection=[
            ("inline_template", "Inline Template"),
            ("qweb", "QWeb"),
            ("qweb_view", "QWeb View"),
        ],
        required=True,
        default="inline_template",
        help="This field allows to select the engine to use for rendering the "
        "template.",
    )

    def _get_ir_model_items(self, models):
        return (
            self.env["ir.model"]
            .sudo()
            .search(
                [
                    ("is_comment_template", "=", True),
                    ("model", "!=", "comment.template"),
                    ("model", "in", models),
                ]
            )
        )

    @api.depends("models")
    def _compute_model_ids(self):
        im_model = self.env["ir.model"]
        for item in self:
            models = im_model.browse()
            if item.models:
                models = self._get_ir_model_items(item.models.split(","))
            item.model_ids = [Command.set(models.ids)]

    @api.constrains("models")
    def check_models(self):
        """Avoid non-existing or not allowed models (is_comment_template=True)"""
        for item in self.filtered("models"):
            models = item.models.split(",")
            res = self._get_ir_model_items(item.models.split(","))
            if not res or len(res) != len(models):
                raise ValidationError(
                    self.env._(f"Some model ({item.models}) not found")
                )

    @api.depends("position", "model_ids")
    def _compute_display_name(self):
        for rec in self:
            name = "{name} ({position})".format(
                name=rec.name,
                position=dict(self._fields["position"].selection).get(rec.position),
            )
            if self.env.context.get("comment_template_model_display"):
                name = "{name} ({models})".format(
                    name=name,
                    models=", ".join(rec.model_ids.mapped("name")),
                )
            rec.display_name = name

    def _search_model_ids(self, operator, value):
        # We cannot use model_ids.model in search() method to avoid access errors
        allowed_items = (
            self.sudo()
            .search([])
            .filtered(lambda x: value in x.model_ids.mapped("model"))
        )
        return [("id", "in", allowed_items.ids)]
