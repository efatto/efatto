openerp.pos_fiscal = function(instance) {
    // loading the namespace of the 'point_of_sale' module
    var QWeb = instance.web.qweb;
    var module = instance.point_of_sale;
    var _t = instance.web._t;

    module.PaymentScreenWidget.include({

        validate_order: function(options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            if(currentOrder.get('orderLines').models.length === 0){
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Empty Order'),
                    'comment': _t('There must be at least one product in your order before it can be validated'),
                });
                return;
            }

            var plines = currentOrder.get('paymentLines').models;
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return;
                }
            }

            if(!this.is_paid()){
                return;
            }

            // If the amount is negative stop. THIS IS THE ONLY CHANGE TO ORIGINAL JS
            if (currentOrder.getTotalTaxIncluded() < 0.00001) {
                this.pos_widget.screen_selector.show_popup('error',{
                    message: _t('Cannot have a negative total amount'),
                    comment: _t('Amount of receipt must always be positive to respect fiscal law.\n\n Please sell another product to make the total amount positive.'),
                });
                return;
            }

            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < this.pos.cashregisters.length; i++) {
                    cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Cannot return change without a cash payment method'),
                        comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return;
                }
            }

            if (this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
            }

            if(options.invoice){
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation',true);
                this.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').destroy();
                });

            }else{
                this.pos.push_order(currentOrder)
                if(this.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    this.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,
                    }));
                    this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }else{
                    this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                }
            }

            // hide onscreen (iOS) keyboard
            setTimeout(function(){
                document.activeElement.blur();
                $("input").blur();
            },250);
        },
    });

    var OrderlineParent = module.Orderline;
    module.Orderline = module.Orderline.extend({
        /**
         * @param attr
         * @param options
         */
        initialize: function (attr, options) {
            OrderlineParent.prototype.initialize.apply(this, arguments);
            this.tax_department = false;
        },

        get_tax_department: function(){
            var self = this;
            var currentOrder = this.pos.get('selectedOrder');
            var ptaxes_ids = this.get_product().taxes_id;
            var tax_amount = false
            if (ptaxes_ids[0] !== false) {
                ptaxes_id = ptaxes_ids[0];
                for (var i = 0; i < this.pos.taxes.length; i++) {
                    if (ptaxes_id === this.pos.taxes[i].id) {
                        tax_amount = this.pos.taxes[i].amount;
                    }
                }
                if(tax_amount === 0.04) {
                    return 1; //ptaxes_ids[i].tax_department; currentOrder.get('orderLines').models.
                }else{
                    if(tax_amount === 0.10) {
                        return 2;
                    }else{
                        if(tax_amount === 0.22) {
                            return 3;
                        }else{
                            return 4;
                            }
                    }
                }
            }

        },

        export_for_printing: function(){

            return {
                quantity:           this.get_quantity(),
                unit_name:          this.get_unit().name,
                price:              this.get_unit_price(),
                discount:           this.get_discount(),
                product_name:       this.get_product().display_name,
                price_display :     this.get_display_price(),
                price_with_tax :    this.get_price_with_tax(),
                price_without_tax:  this.get_price_without_tax(),
                tax:                this.get_tax(),
                product_description:      this.get_product().description,
                product_description_sale: this.get_product().description_sale,
                tax_department:     this.get_tax_department(),
            };
        },
    });
}
