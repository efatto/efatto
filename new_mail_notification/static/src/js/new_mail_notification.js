var qweb = openerp.web.qweb;
var _t = openerp.web._t;
openerp.new_mail_notification =  function(instance){
    instance.web.needaction_notify = instance.web.Widget.extend({
        template: 'WebClient.needaction_systray',
        events: {
        'click .fa-bell-o': 'get_all_data',
        },
        init: function(parent, options){
            this._super(parent);
            this.menu_ids = [];
        },
        get_all_data: function(only_update){
            var self = this;
            this.rpc("/notification/needaction").done(function(r) {
                 self.show_notification(r);
            });
        },
        show_notification: function(result){
            var self = this;
            if( result.length === 0){
                self.getParent().do_notify(_t("Good Job, no new Mail."), '', true);
                return;
            }
            var html = instance.web.qweb.render('WebClient.needaction_list', {'result': result})
            var notification = self.getParent().do_notify(
                    _t("Unread Mails(Click on below link)."), html , true);
            notification.element.find('div.oe_webclient_notification_action a').on('click', function(e) {
                    notification.close();
                    self.getParent().on_menu_action({
                    'action_id':parseInt($(e.currentTarget).attr('id')),
                    'needaction': true
                });
                return false;
            });
        },
    })
    instance.web.WebClient.include({
        show_application: function(){
            this._super();
            var needaction_notify = new instance.web.needaction_notify(this, {});
            needaction_notify.prependTo(window.$('.oe_systray'));
        },
    });
    
};  

