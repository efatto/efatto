odoo.define('calendar_colors' , function (require) {
"use strict";

var CalendarView = require('web_calendar.CalendarView');

CalendarView.include({
    init: function(parent, dataset, fields_view, options){
    	this._super.apply(this, arguments);
        
        if (this.model === 'sale.order') {
            this.color_map = {
                'to_process': 'hyc1',  //'#ffffff',
                'to_evaluate': 'hyc2',  //'#aa309d',
                'production_ready_toproduce': 'hyc3',   //'#f8ca03',
                'production_started': 'hyc4',   //'#59b300',
                'production_done': 'hyc5',   //'#303030',
                'to_receive': 'hyc6',     //'#c70000',
                'to_produce': 'hyc7',     //'#0522ff',
                'to_pack': 'hyc8',        //'#a47c48',
                'partially_delivered': 'hyc9',   //'#1e90ff',
                'delivery_done':  'hyca',    //'#00e07a',
                'available' : 'hycb',     //'#30aa7a',
            }
        }
    }
});
});