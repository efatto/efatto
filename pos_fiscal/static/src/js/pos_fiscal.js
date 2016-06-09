openerp.pos_fiscal = function(instance) {
    // loading the namespace of the 'point_of_sale' module
    var QWeb = instance.web.qweb;
    var module = instance.point_of_sale;
    var _t = instance.web._t;


    var OrderSuper = module.Order;

    module.Order = module.Order.extend({
        addPaymentline: function(cashregister) {
//            res = OrderSuper.prototype.addPaymentline.call(this, cashregister);
            var paymentLines = this.get('paymentLines');
            var newPaymentline = new module.Paymentline({},{cashregister:cashregister, pos:this.pos});
            if(cashregister.journal.type === 'cash'){
                newPaymentline.set_amount( Math.max(this.getDueLeft(),0) );
            }
            paymentLines.add(newPaymentline);
            this.selectPaymentline(newPaymentline);
//            return res
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
                            return 3;
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
