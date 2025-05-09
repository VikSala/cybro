# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.misc import format_duration
from odoo.tools.translate import _

from ..exceptions import SwallableException
from .utils import convert_simple_to_full_parser

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def __parse_field(self, parser_field):
        """Deduct how to handle a field from its parser."""
        return parser_field if isinstance(parser_field, tuple) else (parser_field, None)

    @api.model
    def _jsonify_bad_parser_error(self, field_name):
        raise UserError(_("Wrong parser configuration for field: `%s`") % field_name)

    def _function_value(self, record, function, field_name):
        if function in dir(record):
            method = getattr(record, function, None)
            return method(field_name)
        elif callable(function):
            return function(record, field_name)
        else:
            return self._jsonify_bad_parser_error(field_name)

    @api.model
    def _jsonify_value(self, field, value):
        """Override this function to support new field types."""
        if value is False and field.type != "boolean":
            value = None
        elif field.type == "date":
            value = fields.Date.to_date(value).isoformat()
        elif field.type == "datetime":
            # Ensures value is a datetime
            value = fields.Datetime.to_datetime(value)
            value = value.isoformat()
        elif field.type in ("many2one", "reference"):
            value = value.display_name if value else None
        elif field.type in ("one2many", "many2many"):
            value = [v.display_name for v in value]
        return value

    @api.model
    def _add_json_key(self, values, json_key, value):
        """To manage defaults, you can use a specific resolver."""
        key, sep, marshaller = json_key.partition("=")
        if marshaller == "list":  # sublist field
            if not values.get(key):
                values[key] = []
            values[key].append(value)
        else:
            values[key] = value

    @api.model
    def _jsonify_record(self, parser, rec, root):
        """JSONify one record (rec). Private function called by jsonify."""
        strict = self.env.context.get("jsonify_record_strict", False)
        for field_key in parser:
            field_dict, subparser = rec.__parse_field(field_key)
            function = field_dict.get("function")
            try:
                self._jsonify_record_validate_field(rec, field_dict, strict)
            except SwallableException:
                if not function:
                    # If we have a function we can use it to get the value
                    # even if the field is not available.
                    # If not, well there's nothing we can do.
                    continue
            json_key = field_dict.get("target", field_dict["name"])
            if function:
                try:
                    value = self._jsonify_record_handle_function(
                        rec, field_dict, strict
                    )
                except SwallableException:
                    continue
            elif subparser:
                try:
                    value = self._jsonify_record_handle_subparser(
                        rec, field_dict, strict, subparser
                    )
                except SwallableException:
                    continue
            else:
                field = rec._fields[field_dict["name"]]
                value = rec._jsonify_value(field, rec[field.name])
                resolver = field_dict.get("resolver")
                if resolver:
                    if isinstance(resolver, int):
                        # cached versions of the parser are stored as integer
                        resolver = self.env["ir.exports.resolver"].browse(resolver)
                    value, json_key = self._jsonify_record_handle_resolver(
                        rec, field, resolver, json_key
                    )
            # whatever json value we have found in subparser or not ass a sister key
            # on the same level _fieldname_{json_key}
            if rec.env.context.get("with_fieldname"):
                json_key_fieldname = "_fieldname_" + json_key
                # check if we are in a subparser has already the fieldname sister keys
                fieldname_value = rec._fields[field_dict["name"]].string
                self._add_json_key(root, json_key_fieldname, fieldname_value)
            self._add_json_key(root, json_key, value)
        return root

    def _jsonify_record_validate_field(self, rec, field_dict, strict):
        field_name = field_dict["name"]
        if field_name not in rec._fields:
            if strict:
                # let it fail
                rec._fields[field_name]  # pylint: disable=pointless-statement
            else:
                if not tools.config["test_enable"]:
                    # If running live, log proper error
                    # so that techies can track it down
                    _logger.warning(
                        "%(model)s.%(fname)s not available",
                        {"model": self._name, "fname": field_name},
                    )
                raise SwallableException()
        return True

    def _jsonify_record_handle_function(self, rec, field_dict, strict):
        field_name = field_dict["name"]
        function = field_dict["function"]
        try:
            return self._function_value(rec, function, field_name)
        except UserError as err:
            if strict:
                raise
            if not tools.config["test_enable"]:
                _logger.error(
                    "%(model)s.%(func)s not available",
                    {"model": self._name, "func": str(function)},
                )
                raise SwallableException() from err

    def _jsonify_record_handle_subparser(self, rec, field_dict, strict, subparser):
        field_name = field_dict["name"]
        field = rec._fields[field_name]
        if not (field.relational or field.type == "reference"):
            if strict:
                self._jsonify_bad_parser_error(field_name)
            if not tools.config["test_enable"]:
                _logger.error(
                    "%(model)s.%(fname)s not relational",
                    {"model": self._name, "fname": field_name},
                )
                raise SwallableException()
        value = [self._jsonify_record(subparser, r, {}) for r in rec[field_name]]

        if field.type in ("many2one", "reference"):
            value = value[0] if value else None

        return value

    def _jsonify_record_handle_resolver(self, rec, field, resolver, json_key):
        value = rec._jsonify_value(field, rec[field.name])
        value = resolver.resolve(field, rec)[0] if resolver else value
        if isinstance(value, dict) and "_json_key" in value and "_value" in value:
            # Allow override of json_key.
            # In this case,
            # the final value must be encapsulated into _value key
            value, json_key = value["_value"], value["_json_key"]
        return value, json_key

    def jsonify(self, parser, one=False, with_fieldname=False):
        """Convert the record according to the given parser.

        Example of (simple) parser:
            parser = [
                'name',
                'number',
                'create_date',
                ('partner_id', ['id', 'display_name', 'ref'])
                ('shipping_id', callable)
                ('delivery_id', "record_method")
                ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
            ]

        In order to be consistent with the Odoo API the jsonify method always
        returns a list of objects even if there is only one element in input.
        You can change this behavior by passing `one=True` to get only one element.

        By default the key into the JSON is the name of the field extracted
        from the model. If you need to specify an alternate name to use as
        key, you can define your mapping as follow into the parser definition:

        parser = [
             'field_name:json_key'
        ]

        """
        if one:
            self.ensure_one()
        if isinstance(parser, list):
            parser = convert_simple_to_full_parser(parser)
        resolver = parser.get("resolver")
        if isinstance(resolver, int):
            # cached versions of the parser are stored as integer
            resolver = self.env["ir.exports.resolver"].browse(resolver)
        results = [{} for record in self]
        parsers = {False: parser["fields"]} if "fields" in parser else parser["langs"]
        for lang in parsers:
            translate = lang or parser.get("language_agnostic")
            new_ctx = {}
            if translate:
                new_ctx["lang"] = lang
            if with_fieldname:
                new_ctx["with_fieldname"] = True
            records = self.with_context(**new_ctx) if new_ctx else self
            for record, json in zip(records, results, strict=False):
                self._jsonify_record(parsers[lang], record, json)

        if resolver:
            results = resolver.resolve(results, self)
        return results[0] if one else results

    # HELPERS

    def _jsonify_m2o_to_id(self, fname):
        """Helper to get an ID only from a m2o field.

        Example:

            <field name="name">m2o_id</field>
            <field name="target">m2o_id:rel_id</field>
            <field name="instance_method_name">_jsonify_m2o_to_id</field>

        """
        return self[fname].id

    def _jsonify_x2m_to_ids(self, fname):
        """Helper to get a list of IDs only from a o2m or m2m field.

        Example:

            <field name="name">m2m_ids</field>
            <field name="target">m2m_ids:rel_ids</field>
            <field name="instance_method_name">_jsonify_x2m_to_ids</field>

        """
        return self[fname].ids

    def _jsonify_format_duration(self, fname):
        """Helper to format a Float-like duration to string 00:00.

        Example:

            <field name="name">duration</field>
            <field name="instance_method_name">_jsonify_format_duration</field>

        """
        return format_duration(self[fname])
