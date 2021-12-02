odoo.define('project_task_state_color.calendar', function (require) {
"use strict";

var CalendarView = require('web.CalendarView');

CalendarView.include({
    event_data_transform: function (evt) {
        var r = this._super(evt);
        if (evt.hex_value ) {
            var matches = r.className.match(/o_calendar_color_[0-9]*/g);
                if (matches.length)
                    var original_class_color = (matches[0].replace("calendar", "underline"));
            // set all obj with original_class_color class to evt.hex_value for underline_color_x
            var x = document.getElementsByClassName(original_class_color);
            for (var j=0; j<x.length; j++) {
                x[j].style.backgroundColor = evt.hex_value;
                x[j].classList.remove(original_class_color);
            }
            if (evt.kanban_state === 'done' || evt.stage_id.closed) {
                r.backgroundColor = evt.hex_value_reduced;
            }else{
                r.backgroundColor = evt.hex_value;
            }
        }
        return r;
    },
});

});