openerp.web_cleditor_ept = function(instance) {
	instance.web.form.FieldTextHtml.include({ 
		initialize_content: function() {
	        var self = this;
	        if (! this.get("effective_readonly")) {
	            self._updating_editor = false;
	            this.$textarea = this.$el.find('textarea');
	            var width = ((this.node.attrs || {}).editor_width || 'calc(100% - 4px)');
	            var height = ((this.node.attrs || {}).editor_height || 250);
	            this.$textarea.cleditor({
	                width:      width, // width not including margins, borders or padding
	                height:     height, // height not including margins, borders or padding
	                bodyStyle:  // style to assign to document body contained within the editor
	                            "margin:4px; color:#4c4c4c; font-size:13px; font-family:'Lucida Grande',Helvetica,Verdana,Arial,sans-serif; cursor:text"
	            });
	            this.$cleditor = this.$textarea.cleditor()[0];
	            this.$cleditor.change(function() {
	                if (! self._updating_editor) {
	                    self.$cleditor.updateTextArea();
	                    self.internal_set_value(self.$textarea.val());
	                }
	            });
	            if (this.field.translate) {
	                var $img = $('<img class="oe_field_translate oe_input_icon" src="/web/static/src/img/icons/terp-translate.png" width="16" height="16" border="0"/>')
	                    .click(this.on_translate);
	                this.$cleditor.$toolbar.append($img);
	            }
	        }
	    },
    });
};