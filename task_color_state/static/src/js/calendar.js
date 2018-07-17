openerp.task_color_state = function (instance) {
    instance.web_calendar.CalendarView = instance.web_calendar.CalendarView.extend({
        event_data_transform: function (event) {
            var res = this._super.apply(this, arguments);
//	    //This would go off when there is no color set for hex_value. You could control this too.
//            if (res && res.hasOwnProperty('className')) {
//		//If you would uncomment the next line it would use the default color that is set for the user. (default behaviour from Odoo calendars)
//                //res.className = res.className.substring(0, res.className.indexOf(' calendar_color_'));
//		res.backgroundColor = '#DBDBDB';
//		if(res.title.indexOf('false') > -1)
//		{
//		   res.title = res.title.substring(0, res.title.indexOf(','));
//		}
//            }
        debugger;
        if (event.hex_value ) {
            res.backgroundColor = event.hex_value;
            if (event.kanban_state === 'done') {
                res.backgroundColor = event.hex_value_reduced;
            }else{
                res.backgroundColor = event.hex_value;
            }
        }
        return res;
        }
    });

};