# Copyright 2017 Creu Blanca <https://creublanca.es/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import logging

from odoo.exceptions import ValidationError
from odoo.tests import common

_logger = logging.getLogger(__name__)
try:
    from stdnum import damm, luhn, verhoeff
    from stdnum.iso7064 import mod_11_2, mod_11_10, mod_37_2, mod_37_36, mod_97_10
except (OSError, ImportError) as err:
    _logger.debug(err)


class TestSequenceCheckDigit(common.TransactionCase):
    def get_sequence(self, method):
        return self.env["ir.sequence"].create(
            {
                "name": "Test sequence",
                "implementation": "standard",
                "check_digit_formula": method,
                "padding": "5",
            }
        )

    def test_none(self):
        sequence = self.get_sequence("none")
        self.assertEqual("00001", sequence.next_by_id())

    def test_null(self):
        sequence = self.get_sequence(None)
        self.assertEqual("00001", sequence.next_by_id())

    def test_luhn(self):
        sequence = self.get_sequence("luhn")
        self.assertTrue(luhn.validate(sequence.next_by_id()))

    def test_damm(self):
        sequence = self.get_sequence("damm")
        self.assertTrue(damm.validate(sequence.next_by_id()))

    def test_verhoeff(self):
        sequence = self.get_sequence("verhoeff")
        self.assertTrue(verhoeff.validate(sequence.next_by_id()))

    def test_mod_11_2(self):
        sequence = self.get_sequence("ISO7064_11_2")
        self.assertTrue(mod_11_2.validate(sequence.next_by_id()))

    def test_mod11_10(self):
        sequence = self.get_sequence("ISO7064_11_10")
        self.assertTrue(mod_11_10.validate(sequence.next_by_id()))

    def test_validation(self):
        sequence = self.get_sequence("ISO7064_11_10")
        with self.assertRaises(ValidationError):
            sequence.prefix = "A"
        sequence.prefix = ""

    def test_mod37_2(self):
        sequence = self.get_sequence("ISO7064_37_2")
        sequence.prefix = "A"
        self.assertTrue(mod_37_2.validate(sequence.next_by_id()))

    def test_mod37_36(self):
        sequence = self.get_sequence("ISO7064_37_36")
        self.assertTrue(mod_37_36.validate(sequence.next_by_id()))

    def test_mod97_10(self):
        sequence = self.get_sequence("ISO7064_97_10")
        self.assertTrue(mod_97_10.validate(sequence.next_by_id()))

    def test_no_mode_imported(self):
        sequence = self.get_sequence(None)
        with self.assertRaises(ValidationError):
            sequence.get_check_digit("ABC")
