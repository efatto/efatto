openerp.pos_hotel = function(instance) {
    module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;


/* ********************************************************
Overload: point_of_sale.PosModel
- Overload module.PosModel.initialize function to load extra-data
     - Load 'name' field of model product.product;
     - Load product.template model;
*********************************************************** */
    var _initialize_ = module.PosModel.prototype.initialize;
    module.PosModel.prototype.initialize = function(session, attributes){
        self = this;
        // Add the load of the field product_product.name
        // that is the name of the template
        // Add the load of attribute values
        for (var i = 0 ; i < this.models.length; i++){
            if (this.models[i].model == 'res.partner'){
                this.models[i].fields.push('room_id','folio_id');
            }
        }

        return _initialize_.call(this, session, attributes);
    };
};