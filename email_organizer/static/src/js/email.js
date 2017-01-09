openerp.email_organizer = function (instance) {
    var mail = instance.mail;
    var QWeb = instance.web.qweb;
    mail.ThreadMessage = mail.ThreadMessage.extend({
        template: 'mail.thread.message',
        events: {
                   'click .oe_assign': 'open_wizard',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        open_wizard: function() {
            var self = this;
            var context = {
                       'active_id': this.id,
            };
            var action = {
                            type: 'ir.actions.act_window',
                            res_model: 'wizard.email.organizer',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            target: 'new',
                            context: context,
                    };
            self.do_action(action);
        }

    });
};