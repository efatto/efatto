from odoo.tests.common import SavepointCase


class TestIrMailServer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user1 = cls.user_model.create(
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

    def _create_channel(self, from_user):
        slide_channel_model = self.env["slide.channel"]
        values = {
            "name": "Test channel",
            "channel_type": "training",
        }
        return slide_channel_model.create(values)

    def _create_slide(self, from_user):
        slide_slide_model = self.env["slide.slide"]
        values = {
            "name": "Test slide",
            "slide_type": "webpage",
            "channel_id": self.channel.id,
        }
        return slide_slide_model.create(values)

    def test_01_slide_publish(self):
        self.channel = self._create_channel(self.user1)
        slide = self._create_slide(self.user1)
        self.assertFalse(slide.has_been_published)
        slide.write({"is_published": True})
        self.assertTrue(slide.has_been_published)
