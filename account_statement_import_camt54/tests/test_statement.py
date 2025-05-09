# Copyright 2020 Camptocamp SA
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo.tests.common import TransactionCase
from odoo.tools.misc import file_path


class TestGenerateBankStatement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        eur_currency = cls.env.ref("base.EUR")
        eur_currency.write({"active": True})
        bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL77ABNA0574908765",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL46ABNA0499998748",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank Journal - (test camt)",
                "code": "TBNKCAMT",
                "type": "bank",
                "bank_account_id": bank.id,
                "currency_id": eur_currency.id,
            }
        )

    def _load_statement(self):
        testfile = file_path("account_statement_import_camt/tests/samples/test-camt054")
        with open(testfile, "rb") as datafile:
            camt_file = base64.b64encode(datafile.read())
            self.env["account.statement.import"].create(
                {
                    "statement_filename": "test import",
                    "statement_file": camt_file,
                }
            ).import_file_button()
            bank_st_record = self.env["account.bank.statement"].search(
                [
                    (
                        "name",
                        "in",
                        ["TBNKC Statement 2022-01-26", "20220120000000000000000"],
                    )
                ],
                limit=1,
            )
            statement_lines = bank_st_record.line_ids
            return statement_lines

    def test_statement_import(self):
        self.journal.transfer_line = True
        lines = self._load_statement()
        self.assertEqual(len(lines), 2)
        self.assertAlmostEqual(sum(lines.mapped("amount")), 0)
        self.journal.transfer_line = False
        lines = self._load_statement()
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(sum(lines.mapped("amount")), 5.0)
