openerp.account_move_line_date_search = function(instance) {
    instance.web.account.QuickAddListView.include({
        init: function() {
            this.current_date_from = null;
            this.current_date_to = null;
            return this._super.apply(this, arguments);
        },

        set_change_events: function() {
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_account_select_date_from').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_account_select_date_to').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_account_select_date_from').removeAttr('disabled');
                self.$el.parent().find('.oe_account_select_date_to').removeAttr('disabled');
            });
            this.$el.parent().find('.oe_account_select_date_from').change(function() {
                    self.current_date_from = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_account_select_date_to').change(function() {
                    self.current_date_to = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            },
            return this._super.apply(this, arguments);
        },

        search_by_journal_period: function() {
            if (self.current_date_from !== null) domain.push(["date", ">=", self.current_date_from]);
            if (self.current_date_to !== null) domain.push(["date", "<=", self.current_date_to]);
            return this._super.apply(this, arguments);
        },

    });
};
