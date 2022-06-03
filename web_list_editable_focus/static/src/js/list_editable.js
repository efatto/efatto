openerp.web_mobile_view = function(instance) {
    module = instance.web;
    _t = module._t;

    module.ListView.include({
        keypress_ENTER: function (e) {
            debugger;
            var source_field = $(e.target).closest('[data-fieldname]').attr('data-fieldname');
            var fields_order = this.editor.form.fields_order;
            var field_index  = _(fields_order).indexOf(source_field);
            var fields       = this.editor.form.fields;
            var field;
            do {
                if (++field_index >= fields_order.length) {
                    e.preventDefault();
                    return this._next();
                }
                field = fields[fields_order[field_index]];
            } while (!field.$el.is(':visible'));
            field.focus();
            return $.when();
        },
    });
};