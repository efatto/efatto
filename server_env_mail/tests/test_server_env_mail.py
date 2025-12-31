from odoo.tests.common import TransactionCase


class TestIrMailServer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = cls.env["res.users"].create(
            {
                "login": "user1@somemail.com",
                "email": "user1@somemail.com",
                "partner_id": cls.env["res.partner"].create({"name": "User 1"}).id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ],
                    )
                ],
            }
        )

    def _create_mail(self, from_user):
        MailMessage = self.env["mail.mail"]
        email_values = {
            "email_from": from_user.email,
            "subject": "Hello",
            "email_to": "contact@example.com",
            "reply_to": "contact@example.com",
        }
        return MailMessage.create(email_values)

    def test_01_mail_send(self):
        mail = self._create_mail(self.user1)
        result = mail.send()
        self.assertFalse(result)
