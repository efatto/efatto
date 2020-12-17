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
    _loadColors: function (element, events) {
        var r = this._super(element, events);
        if (this.fieldColor) {
            var fieldName = this.fieldColor;
            _.each(events, function (event) {
                var value = event.record[fieldName];
                var color_index = _.isArray(value) ? value[0] : value;
                //todo map color with numbers?
                event.color_index = color_index;
            });
            this.model_color = this.fields[fieldName].relation || element.model;
        }
        return r;
    },
});

CalendarRenderer.include({
    init: function (parent, state, params) {
        this._super(parent, state, params);
        if (this.model === 'sale.order') {
            this.color_map = {
                'to_process': '#ffffff',
                'to_evaluate': '#aa309d',
                'production_ready_toproduce': '#f8ca03',
                'production_started': '#59b300',
                'production_done': '#303030',
                'to_receive': '#c70000',
                'to_produce': '#0522ff',
                'to_pack': '#a47c48',
                'partially_delivered': '#1e90ff',
                'delivery_done':  '#00e07a',
                'available' : '#30aa7a',
            }
        }
    }
});
});