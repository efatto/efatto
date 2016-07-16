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
        // add links to gantt
        parse_data: function(domains, contexts, group_bys) {
            var self = this,
                datas = [],
                links = [],
                parents = {},
                i,
                item,
                data,
                start,
                item_parent_id,
                item_parent_name;

            this.def_items_ids = [];
            if (group_bys[0] === '' || group_bys[0] === undefined) {
                if (this.attrs.default_group_by !== undefined) {
                    group_bys[0] = this.attrs.default_group_by;
                }
            }
            for (i in this.def_items) {
                if (this.def_items[i][this.attrs.date_start] !== false &&
                    ((this.attrs.date_stop !== undefined &&
                      this.def_items[i][this.attrs.date_stop] !== undefined &&
                      this.def_items[i][this.attrs.date_stop] !== false) ||
                    (this.attrs.date_delay !== undefined &&
                     this.def_items[i][this.attrs.date_delay] !== undefined &&
                     this.def_items[i][this.attrs.date_delay] !== false))) {

                    item = this.def_items[i];
                    data = null;
                    start = null;
                    item_parent_id = 'p' + i;
                    item_parent_name = 'task' + i;

                    this.def_items_ids[item.id] = item;
                    if (group_bys[0] === '' || group_bys[0] === undefined || /* se non c'è un progetto, è un genitore */
                        item[group_bys[0]] === undefined ||
                        item[group_bys[0]] === false) {

                        item_parent_id = 'p' + 0;
                        item_parent_name = 'Gantt View';
                    } else if (item[group_bys[0]] !== undefined) { /* se c'è un progetto, è un figlio del progetto*/
                        for (var j = 0;j < item.parent_ids.length;j++){
                            links.push({id:i*1000+j, source:item.parent_ids[j], target:item.id, type:"0"});
                        }
                        item_parent_id = 'p' + item[group_bys][0];
                        item_parent_name = item[group_bys][1];
                    }

                    if (parents[item_parent_id] === undefined) {
                        parents[item_parent_id] = 1;
                        datas.push({
                            'id': item_parent_id,
                            'text' : item_parent_name,
                            open : true
                        });
                    }

                    start = instance.web.auto_str_to_date(item[this.attrs.date_start]);
                    data = {
                        'id' : item.id,
                        'text': item.name,
                        'start_date' : start,
                        'parent' : item_parent_id,
                    };
                    if (item.sequence !== undefined)
                        data.order = item.sequence;
                    if (this.attrs.progress !== undefined) {
                        data.progress = item[this.attrs.progress] / 100.00;
                    }
                    if (this.attrs.date_stop !== undefined) {
                        var date_stop = instance.web.auto_str_to_date(item[this.attrs.date_stop]);
                        data.end_date = date_stop;
                    } else if (item[this.attrs.date_start + "_end"] !== undefined) {
                        /*
                            Fix for MRP module:
                            no date_stop in attrs, but date_planned_end found on itmes
                        */
                        var date_start_end = instance.web.auto_str_to_date(item[this.attrs.date_start + "_end"]);
                        data.end_date = date_start_end;
                    } else if (this.attrs.date_delay !== undefined) {
                        var unitvalues = ["minute", "hour", "day", "week", "month", "year"];
                        if (unitvalues.indexOf(this.attrs.date_delay) > -1) {
                            gantt.config.duration_unit = this.attrs.date_delay;
                        }
                        data.duration = (item[this.attrs.date_delay] > 0) ? item[this.attrs.date_delay] : 0.1;
                    } else {
                        console.error('Error gantt_improvement E1');
                    }
                    datas.push(data);
                }
            }
            this.draw_gantt(datas, links);
        },
        // change order of task to date_start
        do_search: function (domains, contexts, group_bys) {
            var filter = [],
                self = this;

            this.def_last_domains = domains;
            this.def_last_contexts = contexts;
            this.def_last_group_bys = group_bys;
            this.reload_gantt();

            if (this.attrs.date_stop !== undefined) {
                // We know end date
                filter = [
                    '&',
                        '&',
                            '|',
                                '|',
                                    '&',
                                        [this.attrs.date_start, '>=', this.def_gantt_date_start],
                                        [this.attrs.date_start, '<=', this.def_gantt_date_end],
                                    '&',
                                        [this.attrs.date_stop, '>=', this.def_gantt_date_start],
                                        [this.attrs.date_stop, '<=', this.def_gantt_date_end],
                                '&',
                                    [this.attrs.date_start, '<=', this.def_gantt_date_start],
                                    [this.attrs.date_stop, '>=', this.def_gantt_date_end],
                            '&',
                                [this.attrs.date_start, '!=', null],
                                [this.attrs.date_stop, '!=', null],
                ];
            } else if (this.attrs.date_delay !== undefined) {
                // We don't know end date but, we know date delay
                /*
                    Date delay : @TODO Reproduce this filter in good notation
                    (this.attrs.date_start > this.date_start
                    && this.attrs.date_start > this.date_end) ||
                    (this.attrs.date_start < this.date_start &&
                    (this.attrs.date_start + this.attrs.date_delay) > this.date_start)
                */
                filter = [
                ];
            }
            if (domains.length > 0)
                filter = filter.concat(domains);
            else
                filter.push([this.attrs.date_start, '!=', null]);

            return (
                new instance.web.Model(this.dataset.model)
                    .query()
                    .filter(filter)
                    .order_by('date_start, priority desc, sequence, name, id')
                    .all()
                    .then(function (result) {
                        self.def_items = result;
                        self.parse_data(domains, contexts, group_bys);
                    })
            );
        },
    });
};