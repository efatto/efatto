openerp.project_task_state_color = function (instance) {
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

        if (event.hex_value ) {
            var matches = res.className.match(/calendar_color_[0-9]*/g);
                if (matches.length)
                    var original_class_color = (matches[0].replace("calendar", "underline"));
            // set all obj with original_class_color class to event.hex_value for underline_color_x
            var x = document.getElementsByClassName(original_class_color);
            for (var j=0; j<x.length; j++) {
                x[j].style.backgroundColor = event.hex_value;
                x[j].classList.remove(original_class_color);
            }
            if (event.kanban_state === 'done' || event.state === 'done') {
                res.backgroundColor = event.hex_value_reduced;
            }else{
                res.backgroundColor = event.hex_value;
            }
        }
        return res;
        }
    });

};