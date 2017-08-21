import datetime
import dateutil.relativedelta as relativedelta
import logging

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp import tools, api
from urllib import urlencode, quote as quote

_logger = logging.getLogger(__name__)


def format_tz(pool, cr, uid, dt, tz=False, format=False, context=None):
    context = dict(context or {})
    if tz:
        context['tz'] = tz or pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz'] or "UTC"
    timestamp = datetime.datetime.strptime(dt, tools.DEFAULT_SERVER_DATETIME_FORMAT)
    ts = fields.datetime.context_timestamp(cr, uid, timestamp, context)

    # Babel allows to format datetime in a specific language without change locale
    # So month 1 = January in English, and janvier in French
    # Be aware that the default value for format is 'medium', instead of 'short'
    #     medium:  Jan 5, 2016, 10:20:31 PM |   5 janv. 2016 22:20:31
    #     short:   1/5/16, 10:20 PM         |   5/01/16 22:20
    if context.get('use_babel'):
        # Formatting available here : http://babel.pocoo.org/en/latest/dates.html#date-fields
        from babel.dates import format_datetime
        return format_datetime(ts, format or 'medium', locale=context.get("lang") or 'en_US')

    if format:
        return ts.strftime(format)
    else:
        lang = context.get("lang")
        lang_params = {}
        if lang:
            res_lang = pool.get('res.lang')
            ids = res_lang.search(cr, uid, [("code", "=", lang)])
            if ids:
                lang_params = res_lang.read(cr, uid, ids[0], ["date_format", "time_format"])
        format_date = lang_params.get("date_format", '%B-%d-%Y')
        format_time = lang_params.get("time_format", '%I-%M %p')

        fdate = ts.strftime(format_date).decode('utf-8')
        ftime = ts.strftime(format_time).decode('utf-8')
        return "%s %s%s" % (fdate, ftime, (' (%s)' % tz) if tz else '')


def format_amount(pool, cr, uid, amount, currency, context):
    fmt = "%.{0}f".format(2)
    lang = context.get("lang") or 'en_US'
    if lang:
        res_lang = pool.get('res.lang')
        ids = res_lang.search(cr, uid, [("code", "=", lang)])
        if ids:
            lang_id = res_lang.browse(cr, uid, ids[0])
            formatted_amount = lang_id.format(
                fmt, currency.round(amount), grouping=True, monetary=True) \
                .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'\u2011')

    pre = post = u''
    if currency.position == 'before':
        pre = u'{symbol}\N{NO-BREAK SPACE}'.format(
            symbol=currency.symbol or '')
    else:
        post = u'\N{NO-BREAK SPACE}{symbol}'.format(
            symbol=currency.symbol or '')

    return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class EmailTemplate(osv.osv):
    _inherit = "email.template"

    def render_template_batch(self, cr, uid, template, model, res_ids,
                              context=None, post_process=False):
        """Render the given template text, replace mako expressions ``${expr}``
           with the result of evaluating these expressions with
           an evaluation context containing:

                * ``user``: browse_record of the current user
                * ``object``: browse_record of the document record this mail is
                              related to
                * ``context``: the context passed to the mail composition wizard

           :param str template: the template text to render
           :param str model: model name of the document record this mail is related to.
           :param int res_ids: list of ids of document records those mails are related to.
        """
        if context is None:
            context = {}
        res_ids = filter(None, res_ids)  # to avoid browsing [None] below
        results = dict.fromkeys(res_ids, u"")

        # try to load the template
        try:
            template = mako_template_env.from_string(tools.ustr(template))
        except Exception:
            _logger.exception("Failed to load template %r", template)
            return results

        # prepare template variables
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        records = self.pool[model].browse(cr, uid, res_ids, context=context) or [
            None]
        variables = {
            'format_tz': lambda dt, tz=False, format=False,
                                context=context: format_tz(self.pool, cr, uid, dt,
                                                           tz, format, context),
            'format_amount': lambda amount, currency,
                                    context=context: format_amount(self.pool,
                                                                   cr, uid,
                                                                   amount,
                                                                   currency,
                                                                   context),
            'user': user,
            'ctx': context,  # context kw would clash with mako internals
        }
        for record in records:
            res_id = record.id if record else None
            variables['object'] = record
            try:
                render_result = template.render(variables)
            except Exception:
                _logger.exception(
                    "Failed to render template %r using values %r" % (
                    template, variables))
                render_result = u""
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result

        if post_process:
            for res_id, result in results.iteritems():
                results[res_id] = self.render_post_process(cr, uid, result,
                                                           context=context)
        return results