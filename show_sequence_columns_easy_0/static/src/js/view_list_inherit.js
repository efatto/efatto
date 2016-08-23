view_list_inherit = function(instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.View.include({
        load_view: function(context) {
            var self = this;
            var view_loaded_def;
            if (this.embedded_view) {
                view_loaded_def = $.Deferred();
                $.async_when().done(function() {
                    view_loaded_def.resolve(self.embedded_view);
                });
            }else {
                if (! this.view_type){
                    console.warn("view_type is not defined", this);
                    }
                view_loaded_def = instance.web.fields_view_get({
                    "model": this.dataset._model,
                    "view_id": this.view_id,
                    "view_type": this.view_type,
                    "toolbar": !!this.options.$sidebar,
                    "context": this.dataset.get_context(),
                });
            }
            return this.alive(view_loaded_def).then(function(r) {
                self.fields_view = r;
                // add css classes that reflect the (absence of) access rights
                self.$el.addClass('oe_view')
                    .toggleClass('oe_cannot_create', !self.is_action_enabled('create'))
                    .toggleClass('oe_cannot_edit', !self.is_action_enabled('edit'))
                    .toggleClass('oe_cannot_delete', !self.is_action_enabled('delete'));
                return $.when(self.view_loading(r)).then(function() {
                    self.render_fields_show();
                    self.trigger('view_loaded', r);
                });
            });
        },
        render_fields_show: function () {
            var self = this;
            if (typeof(self.model) != 'undefined'){
                if ($('.choose_field_show').length <= 0 && !$('.oe_searchview').is(':hidden')) {
                    var show_field_model = new instance.web.Model('show.fields');
                    QWeb.add_template("/show_sequence_columns_easy_0/static/src/xml/my_control.xml");
                    $('.oe_view_manager_header col[width="30%"]').css({'width': '38%'});
                    show_field_model.get_func('action')({'model_name': self.model, 'user_id': self.session.uid}, 'select').then(function (result){
                        var data_show_field = result.data;
                        self.data_show_field = data_show_field;
                        var all_fields_of_model = result.fields;
                        self.all_fields_of_model = all_fields_of_model;
                        var field_visible = data_show_field.hasOwnProperty('fields_show') && data_show_field['fields_show'] ? eval(data_show_field['fields_show']) : _.pluck(self.visible_columns, 'name');
                        var fields_sequence = data_show_field.hasOwnProperty('fields_sequence') && data_show_field['fields_sequence'] ? JSON.parse(data_show_field['fields_sequence']) : {}
                        var list_data = [];
                        var list_field_checked = [];
                        for (var field_name in all_fields_of_model){
                            var field_obj = all_fields_of_model[field_name];
                            var data = {value: field_name, string: field_obj.string}
                            if (field_visible.indexOf(field_name) >= 0){
                                data['checked'] = 'checked';
                                if (fields_sequence.hasOwnProperty(field_name)){
                                    data['sequence'] = fields_sequence[field_name];
                                }
                                list_field_checked.push(data);
                            }
                            list_data.push(data);
                        }
                        list_data = _.sortBy(list_data, function (o){return o.sequence});
                        self.list_field_checked = _.sortBy(list_field_checked, function (o){return o.sequence});
                        var options = {};
                        options['suggestion'] = list_data;
                        options['attrs'] = {color: data_show_field.color || 'check-primary'};
                        if (typeof(QWeb.templates['ShowField']) != 'undefined'){
                            var tem = QWeb.render('ShowField', {data: options});
                            $('.oe_view_manager_switch').css({'float': 'right'});
                            $('.oe_view_manager_pager').after(tem);
                            $('.oe_view_manager_pager').css({'float': 'left'})
                        }
                        $(".toggle_select_field").click(function() {
                            $(".text_suggestion").toggle();
                        });

                        $(".sequence").change(function () {
                            $(this).parent().prevAll('input').attr({'sequence': $(this).val()});
                        });
                        self.setting_fields_show();
                        self.update_show_fields();
                    });
                }else if($('.oe_searchview').is(':hidden')){
                    $('.choose_field_show').remove();
                }
            }
        },
        update_show_fields: function () {
            var self = this;
            $('a[action="update"]').click(function () {
                var fields = []
                var sequence = {}
                $('.suggestion input:checked').each(function () {
                    fields.push($(this).val());
                    _seq = $(this).attr('sequence') || false;
                    if (_seq){
                        sequence[$(this).attr('id')] = parseInt(_seq);
                    }
                });
                new instance.web.Model('show.fields').get_func('action')({'model_name': self.model, 'fields_show': fields,
                'user_id': self.session.uid, 'fields_sequence': JSON.stringify(sequence)}, 'update').then(function (result) {
                    location.reload();
                });
            });
        },
        setting_fields_show: function () {
            var self = this;
            $(".fields_setting").click(function () {
                var $form_show = $(QWeb.render('FormShowField', self.data_show_field));
                $form_show.find('input[name="color"][value="'+(self.data_show_field.color || 'check-primary')+'"]').attr('checked', true);
                if (self.data_show_field.fix_header_list_view){
                    $form_show.find('#fix_header_list_view').attr('checked', true);
                }
                $form_show.insertAfter('body');
                $('.close-field-show').click(function () {
                    $form_show.remove();
                });
                $form_show.find('a[action="update"]').click(function () {
                    var data = {color: $form_show.find('input[name="color"]:checked').val(),
                                fix_header_list_view: false, model_name: self.model,
                                user_id: self.session.uid}
                    if ($form_show.find('#fix_header_list_view').is(':checked')){
                        data.fix_header_list_view = true;
                    }
                    new instance.web.Model('show.fields').get_func('action')(data, 'update').then(function (result) {
                        location.reload();
                    });
                });
            });
        }
    });

   instance.web.ListView.include({
        view_loading: function(r) {
            if (this.hasOwnProperty('list_field_checked')){
                var all_fields_of_model = this.all_fields_of_model;
                var field = {};
                var children = [];
                for (_field in this.list_field_checked){
                    _field = this.list_field_checked[_field];
                    children.push({attrs: {modifiers: "", name: _field.value}, children: [], tag: "field"});
                    field[_field.value] = all_fields_of_model[_field.value]
                }
                for (_field in r.arch.children){
                    _field = r.arch.children[_field]
                    if (!field.hasOwnProperty(_field.attrs.name)){
                        field[_field.attrs.name] = all_fields_of_model[_field.attrs.name]
                        children.push(_field);
                    }
                }
                r.fields = field;
                r.arch.children = children;
            }
            return this._super(r);
        }
    });
};

openerp.show_sequence_columns_easy_0 = function(instance) {
    view_list_inherit(instance);
};
