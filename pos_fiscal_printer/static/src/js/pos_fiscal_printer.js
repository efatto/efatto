openerp.pos_fiscal_printer = function(instance) {
    // loading the namespace of the 'point_of_sale' module
    var module = instance.point_of_sale;
    var _t = instance.web._t;
    
    module.ReceiptScreenWidget.include({
        
        show: function(){
            var self = this;

            this.hidden = false;
            if(this.$el){
                this.$el.show();
            }

            if(this.pos_widget.action_bar.get_button_count() > 0){
                this.show_action_bar();
            }else{
                this.hide_action_bar();
            }
            
            // we add the help button by default. we do this because the buttons are cleared on each refresh so that
            // the button stay local to each screen
            this.pos_widget.left_action_bar.add_new_button({
                    label: _t('Help'),
                    icon: '/point_of_sale/static/src/img/icons/png48/help.png',
                    click: function(){ self.help_button_action(); },
                });

            var self = this;
            var cashier_mode = this.pos_widget.screen_selector.get_user_mode() === 'cashier';

            this.pos_widget.set_numpad_visible(this.show_numpad && cashier_mode);
            this.pos_widget.set_leftpane_visible(this.show_leftpane);
            this.pos_widget.set_left_action_bar_visible(this.show_leftpane && !cashier_mode);
            this.pos_widget.set_cashier_controls_visible(cashier_mode);

            if(cashier_mode && this.pos.iface_self_checkout){
                this.pos_widget.client_button.show();
            }else{
                this.pos_widget.client_button.hide();
            }
            if(cashier_mode){
                this.pos_widget.close_button.show();
            }else{
                this.pos_widget.close_button.hide();
            }
            
            this.pos_widget.username.set_user_mode(this.pos_widget.screen_selector.get_user_mode());

            this.pos.barcode_reader.set_action_callback({
                'cashier': self.barcode_cashier_action ? function(ean){ self.barcode_cashier_action(ean); } : undefined ,
                'product': self.barcode_product_action ? function(ean){ self.barcode_product_action(ean); } : undefined ,
                'client' : self.barcode_client_action ?  function(ean){ self.barcode_client_action(ean);  } : undefined ,
                'discount': self.barcode_discount_action ? function(ean){ self.barcode_discount_action(ean); } : undefined,
            });
    
            this.add_action_button({
                label: _t('Next Order'),
                icon: '/point_of_sale/static/src/img/icons/png48/go-next.png',
                click: function() { self.finishOrder(); },
            });
        },
    });
}
