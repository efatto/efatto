openerp.project = function(openerp) {
//    if is a mobile device, ...
    openerp.web_kanban.KanbanView.include({
        project_remove_focus: function() {
            var self = this;
            var elelist = self.getElementsByTagName("oe_searchview_facets");
            for(i=0; i < elelist.length; i++){
                elelist[i].setAttribute("onfocus","this.blur()");
            }
        }
    }
}
