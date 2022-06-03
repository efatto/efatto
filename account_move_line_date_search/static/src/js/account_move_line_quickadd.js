openerp.account_move_line_date_search = function(instance) {
    var QWeb = instance.web.qweb;
    instance.web.account.QuickAddListView.include({
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.current_date_from = null;
            this.current_date_to = null;
            this.account_credit = false;
            this.account_debit = false;
        },

        start: function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().find('.oe_account_select_journal').change(function() {
                    self.current_journal = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_account_select_period').change(function() {
                    self.current_period = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_account_select_date_from').change(function() {
                    self.current_date_from = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find('.oe_account_select_date_to').change(function() {
                    self.current_date_to = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.$el.parent().find(".oe_account_credit").click(function() {
                    self.search_credit();
                });
            this.$el.parent().find(".oe_account_debit").click(function() {
                    self.search_debit();
                });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_account_select_journal').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_account_select_period').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_account_select_journal').removeAttr('disabled');
                self.$el.parent().find('.oe_account_select_period').removeAttr('disabled');
            });
            var mod = new instance.web.Model("account.move.line", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [['journal_id','period_id'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_journal = result['journal_id'];
            }));
            defs.push(mod.call("list_journals", []).then(function(result) {
                self.journals = result;
            }));
            defs.push(mod.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));
            return $.when(tmp, defs);
        },

        search_debit: function() {
            var self = this;
            last_domain = self.last_domain;
            if (this.account_debit === false) {
                this.account_debit = true;
                last_domain.push(['account_id.type', '=', 'payable']);
                self.$el.parent().find(".oe_account_debit").removeClass('oe_highlight').removeAttr("oe_highlight");
            } else {
                this.account_debit = false;
                self.$el.parent().find(".oe_account_debit").addClass("oe_highlight").attr("oe_highlight", "");
                last_domain.splice(last_domain.indexOf(['account_id.type', '=', 'payable']));
            }
            self.do_search(last_domain, self.last_context, self.last_group_by);
        },

        search_credit: function() {
            var self = this;
            last_domain = self.last_domain;
            if (this.account_credit === false) {
                this.account_credit = true;
                last_domain.push(['account_id.type', '=', 'receivable']);
                self.$el.parent().find(".oe_account_credit").removeClass('oe_highlight').removeAttr("oe_highlight");
            } else {
                this.account_credit = false;
                self.$el.parent().find(".oe_account_credit").addClass("oe_highlight").attr("oe_highlight", "");
                last_domain.splice(last_domain.indexOf(['account_id.type', '=', 'receivable']));
            }
            self.do_search(last_domain, self.last_context, self.last_group_by);
        },

        search_by_journal_period: function() {
            var self = this;
            var domain = [];
            if (self.current_date_from) domain.push(['date', '>=', self.current_date_from]);
            if (self.current_date_to) domain.push(['date', '<=', self.current_date_to]);
            if (self.current_journal !== null) domain.push(["journal_id", "=", self.current_journal]);
            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);
            self.last_context["journal_id"] = self.current_journal === null ? false : self.current_journal;
            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;
            self.last_context["journal_type"] = self.current_journal_type;
            self.last_context["currency"] = self.current_journal_currency;
            self.last_context["analytic_journal_id"] = self.current_journal_analytic;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },

    });
};
