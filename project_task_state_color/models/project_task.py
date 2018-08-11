# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions


class ProjectProject(models.Model):
    _inherit = 'project.project'

    hex_value = fields.Char()


class ProjectTask(models.Model):
    _inherit = 'project.task'

    hex_value = fields.Char(related='project_id.hex_value', readonly=True)
    hex_value_reduced = fields.Char(compute='_get_hex_task_value')

    @staticmethod
    def colorscale(hexstr, scalefactor):
        """
        Scales a hex string by ``scalefactor``. Returns scaled hex string.

        To darken the color, use a float value between 0 and 1.
        To brighten the color, use a float value greater than 1.

        # >>> colorscale("#DF3C3C", .5)
        #6F1E1E
        # >>> colorscale("#52D24F", 1.6)
        #83FF7E
        # >>> colorscale("#4F75D2", 1)
        #4F75D2
        """

        def clamp(val, minimum=0, maximum=255):
            if val < minimum:
                return minimum
            if val > maximum:
                return maximum
            return val

        hexstr = hexstr.strip('#')

        if scalefactor < 0 or len(hexstr) != 6:
            return hexstr

        r, g, b = int(hexstr[:2], 16),\
            int(hexstr[2:4], 16), int(hexstr[4:], 16)

        r = clamp(r * scalefactor)
        g = clamp(g * scalefactor)
        b = clamp(b * scalefactor)

        return "#%02x%02x%02x" % (r, g, b)

    @api.multi
    def _get_hex_task_value(self):
        for task in self:
            if task.hex_value:
                task.hex_value_reduced = task.colorscale(
                        task.hex_value, .5)
