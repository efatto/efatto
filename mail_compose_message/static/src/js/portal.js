openerp.mail_compose_message = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail;

/* ********************************************************
Overload: mail.Wall
- Overload mail.Wall.start function to hide button for some
     groups
*********************************************************** */
    var MailWallSuper = mail.Wall;
    mail.Wall = mail.Wall.extend({
        hide_composeElement:function(){
//            var res = MailWallSuper.prototype.start.call(this);
            debugger;
            var composeElement = this.$el.find('.mail_compose_message');
            var Users = new openerp.web.Model('res.users');
                Users.call('has_group', ['base.group_portal']).done(function(is_portal) {
                    if (is_portal) {
                        composeElement.$el.hide();
                    }else{
                        composeElement.$el.show();
                    },
                });
                this._super.apply(this, arguments);
//            return res;
            },
    });
*****
//    var _start_ = mail.Wall.prototype.start;
//    mail.Wall.prototype.start = function(){
//        self = this;
//        debugger;
//        var composeElement = this.$el.find('.mail_compose_message');
//        if(openerp.web && openerp.web.UserMenu) {
//            openerp.web.UserMenu.include({
//                do_update: function(){
//                    var self = this;
//                    var Users = new openerp.web.Model('res.users');
//                    Users.call('has_group', ['base.group_portal']).done(function(is_portal) {
//                        if (is_portal) {
//                            composeElement.$el.hide();
//                        }else{
//                            composeElement.$el.show();
//                        },
//                    });
//                    return this._super.apply(this, arguments);
//                },
//            });
//        };
//        return _start_.call(this);
//    };
};