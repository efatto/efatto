openerp.mail_compose_message = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail;

/* ********************************************************
Overload: mail.Wall
- Overload mail.Wall.start function to hide button for
     portal group users
*********************************************************** */
    var MailWallSuper = mail.Wall;
    mail.Wall = mail.Wall.extend({
        hide_composeElement:function(){
            var composeElement = this.$el.find('.mail_compose_message');
            var Users = new openerp.web.Model('res.users');
                Users.call('has_group', ['base.group_portal']).done(function(is_portal) {
                    if (is_portal) {
                        composeElement.hide();
                    }else{
                        composeElement.show();
                    }
                });
        },
        start: function () {
            var res = MailWallSuper.prototype.start.call(this);
            this.hide_composeElement();
            return res;
        },
    });

};