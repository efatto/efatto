openerp.sync_mail_notification = function (session){
    var QWeb = session.web.qweb;
    var _t = session.web._t;

    var mail = session.mail;

    mail.Widget.include({
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            /* Auto Fetch New Messages */
            var context= new session.web.CompoundContext();
            var model = new session.web.DataSet(this, 'mail.notification', context);
            this.auto_refresh(context, model);
        },
        auto_refresh: function(context, model){
			/* Auto Fetch New Messages */
            var auto_refresh = setInterval(function (){
                model.call("get_message_notification",[]).done(function(emails) {
                    _.each(emails, function(email){
                        var image_url = openerp.session.url('/web/binary/image', {model:'res.company', field: 'logo', id: email['company_id']});
                        model.call('write', [email['id'], {'is_notified': true}]).then(function(result){});
                        Notification.requestPermission(function(permission){
                            var notification = new Notification(email['email_from'],{body: email['subject'], icon: image_url, dir:'auto'});
                            setTimeout(function(){
                                notification.close();
                            },5000);
                        });
                    });
                });
            },60000); 
        }
    });
}

