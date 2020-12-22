odoo.define('sale_order_calendar_state.CalendarColors' , function (require) {
"use strict";
var CalendarRenderer = require('web.CalendarRenderer');
var CalendarModel = require('web.CalendarModel');

CalendarModel.include({
    load: function (params) {
        var self = this;
        if (params.modelName == 'sale.order') {
            params.fieldColor = 'color';
        }
        return this._super(params);
    },
});

CalendarRenderer.include({
    getColor: function (key) {
        if (!key) {
            return;
        }
        if (this.color_map[key]) {
            return Math.abs(this.color_map[key]);
        }
        if (typeof key === 'number' && key < 0) {
            return Math.abs(key);
        }
        return this._super(key);
    },
    init: function (parent, state, params) {
        this._super(parent, state, params);
        if (this.model === 'sale.order') {
            this.color_map = {
                'to_process': -301,  //'#ffffff',
                'to_evaluate': -302,  //'#aa309d',
                'to_evaluate_production': -302,  //'#aa309d',
                'to_produce': -307,     //'#0522ff',
                'to_receive': -306,     //'#c70000',
                'production_ready': -303,   //'#f8ca03',
                'production_started': -304,   //'#59b300',
                'to_pack': -308,        //'#a47c48',
                'production_done': -305,   //'#303030',
                'partially_delivered': -309,   //'#1e90ff',
                'delivery_done':  -310,    //'#00e07a',
                'available' : -311,     //'#30aa7a',
                'invoiced': -312,
                'shipped': -313,
            }
        }
    }
});
});