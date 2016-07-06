/*---------------------------------------------------------
 * OpenERP gantt_improvement ext
 *---------------------------------------------------------*/
openerp.gantt_improvement_ext = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt,
        QWeb = instance.web.qweb,
        attrs = null,
        last_r = null;
//
//    instance.web.views.add('gantt', 'instance.gantt_improvement.GanttView');

    var GanttViewSuper = instance.gantt_improvement.GanttView;
    instance.gantt_improvement.GanttView = instance.gantt_improvement.GanttView.extend({
        reload_button: function () {
            var date_start,
                date_stop;

            date_start_array = document.getElementById('gantt_improvement_date_start').value.split("-"); /* yyyy-mm-dd -> yyyy-dd-mm*/
            date_stop_array = document.getElementById('gantt_improvement_date_stop').value.split("-");
            date_start = date_start_array[0] + "-" + date_start_array[2] + "-" + date_start_array[1];
            date_stop = date_stop_array[0] + "-" + date_stop_array[2] + "-" + date_stop_array[1];
            if (date_start !== '' && date_start !== null && date_stop !== '' && date_stop !== null) {
                this.def_gantt_date_start = new Date(date_start);
                this.def_gantt_date_end = new Date(date_stop);
                gantt.config.start_date = this.def_gantt_date_start;
                gantt.config.end_date = this.def_gantt_date_end;
            }
            this.reload();
        },
    });
};