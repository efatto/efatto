openerp.pos_hotel = function(instance) {
    module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;


/* ********************************************************
Overload: point_of_sale.PosDB
- Overload module.PosModel._partner_search_string function to search room_id
*********************************************************** */
    var PosDBSuper = module.PosDB;

    module.PosDB = module.PosDB.extend({
//            res = OrderSuper.prototype.addPaymentline.call(this, cashregister);
//            return res
        _partner_search_string: function(partner){
            var str =  partner.name;
            if(partner.ean13){
                str += '|' + partner.ean13;
            }
            if(partner.room_id){
                str += '|' + partner.room_id;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
        },
    });
/* ********************************************************
Overload: point_of_sale.PosModel
- Overload module.PosModel.initialize function to load extra-data
     - Load 'folio' and 'room' field of model res.partner;
*********************************************************** */
    var _initialize_ = module.PosModel.prototype.initialize;
    module.PosModel.prototype.initialize = function(session, attributes){
        self = this;
        // Add the load of the field res_partner.room_id
        // that is the name of the template
        // Add the load of attribute values
        for (var i = 0 ; i < this.models.length; i++){
            if (this.models[i].model == 'res.partner'){
                this.models[i].fields.push('room_id','folio_id');
            }
        }

        return _initialize_.call(this, session, attributes);
    };
/* ********************************************************
Overload: point_of_sale.module.Order
- Overload module.Order.export_for_printing function to load extra-data
     - Load 'room' field of model res.partner;
*********************************************************** */
    var ModuleOrderSuper = module.Order;
    module.Order = module.Order.extend({
        export_for_printing:function(){
            var res = ModuleOrderSuper.prototype.export_for_printing.call(this);
            debugger;
            var client  = this.get('client');
            var room = '';
            if (client){
                if (client.room_id){
                    room = client.room_id[1];
                }
            }
            res.room = room;

            return res;
        },
        export_as_JSON:function(){
            var res = ModuleOrderSuper.prototype.export_as_JSON.call(this);

            return res;
        },
    });
};