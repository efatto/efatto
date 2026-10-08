import {CalendarArchParser} from "@web/views/calendar/calendar_arch_parser";
import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {CalendarModel} from "@web/views/calendar/calendar_model";
import {CalendarYearPopover} from "@web/views/calendar/calendar_year/calendar_year_popover";
import {CalendarYearRenderer} from "@web/views/calendar/calendar_year/calendar_year_renderer";
import {getColor} from "@web/views/calendar/colors";
import {patch} from "@web/core/utils/patch";

// Custom colors defined in static/src/css/calendar.scss. Values are kept
// negative on purpose: they are the "absolute" index that has to be used as
// the CSS class suffix (o_calendar_color_<index>).
const SALE_ORDER_COLOR_MAP = {
    blocked: -321,
    to_process: -301,
    to_evaluate: -301,
    to_evaluate_production: -301,
    to_produce: -302,
    to_receive: -302,
    production_planned: -302,
    production_ready: -302,
    production_started: -303,
    to_pack: -303,
    to_assembly: -304,
    to_submanufacture: -305,
    to_test: -306,
    delivery_ready: -302,
    production_done: -310,
    partially_delivered: -308,
    delivery_done: -307,
    has_ddt: -311,
    available: -301,
    invoiced: -309,
    shipped: -301,
};

/**
 * Compute the color index of a sale.order calendar record.
 *
 * The `color` field of sale.order is a negative integer (see
 * `sale.order._compute_color`), while the color index also accepts the
 * `calendar_state` selection value. Both are mapped to the custom color
 * indexes defined in calendar.scss.
 *
 * @param {number|string} key
 * @returns {number|string|false}
 */
function getSaleOrderColor(key) {
    if (!key) {
        return false;
    }
    if (SALE_ORDER_COLOR_MAP[key]) {
        return Math.abs(SALE_ORDER_COLOR_MAP[key]);
    }
    if (typeof key === "number") {
        return Math.abs(key);
    }
    return getColor(key);
}

/**
 * Replace the color class computed by the default renderer by the custom one.
 *
 * @param {string[]} classes
 * @param {number|string|false} color
 * @returns {string[]}
 */
function replaceColorClass(classes, color) {
    const index = classes.findIndex((className) =>
        className.startsWith("o_calendar_color_")
    );
    if (index >= 0) {
        classes.splice(index, 1);
    }
    if (typeof color === "number") {
        classes.push(`o_calendar_color_${color}`);
    } else if (typeof color !== "string") {
        classes.push("o_calendar_color_0");
    }
    return classes;
}

patch(CalendarArchParser.prototype, {
    parse(arch, models, modelName) {
        const archInfo = super.parse(arch, models, modelName);
        if (modelName === "sale.order") {
            // The calendar view declares `color="calendar_state"`, but the
            // real color is stored in the `color` field. Force the field used
            // to color the events to `color`.
            archInfo.fieldMapping.color = "color";
            for (const filterInfo of Object.values(archInfo.filtersInfo)) {
                // Calendar_state is a selection, not a relation: without a
                // related model the model would try to fetch a color field on
                // an undefined model. The filter color is taken from the
                // record color instead (see CalendarModel.addFilterFields).
                filterInfo.colorFieldName = null;
            }
        }
        return archInfo;
    },
});

patch(CalendarModel.prototype, {
    normalizeRecord(rawRecord) {
        const record = super.normalizeRecord(rawRecord);
        if (this.meta.resModel === "sale.order") {
            record.colorIndex = getSaleOrderColor(record.colorIndex);
        }
        return record;
    },
});

patch(CalendarCommonRenderer.prototype, {
    eventClassNames(info) {
        const classes = super.eventClassNames(info);
        if (this.props.model.resModel === "sale.order") {
            const record = this.props.model.records[info.event.id];
            return replaceColorClass(
                classes,
                getSaleOrderColor(record && record.colorIndex)
            );
        }
        return classes;
    },
    openPopover(target, record) {
        if (this.props.model.resModel !== "sale.order") {
            return super.openPopover(target, record);
        }
        const color = getSaleOrderColor(record && record.colorIndex);
        this.popover.open(
            target,
            this.getPopoverProps(record),
            `o_cw_popover card o_calendar_color_${typeof color === "number" ? color : 0}`
        );
    },
});

patch(CalendarYearRenderer.prototype, {
    eventClassNames(info) {
        const classes = super.eventClassNames(info);
        if (this.props.model.resModel === "sale.order") {
            const record = this.props.model.records[info.event.id];
            return replaceColorClass(
                classes,
                getSaleOrderColor(record && record.colorIndex)
            );
        }
        return classes;
    },
});

patch(CalendarYearPopover.prototype, {
    getRecordClass(record) {
        if (this.props.model.resModel !== "sale.order") {
            return super.getRecordClass(record);
        }
        const color = getSaleOrderColor(record && record.colorIndex);
        return typeof color === "number" ? `o_calendar_color_${color}` : "";
    },
    getRecordStyle(record) {
        if (this.props.model.resModel !== "sale.order") {
            return super.getRecordStyle(record);
        }
        const color = getSaleOrderColor(record && record.colorIndex);
        return typeof color === "string" ? `background-color: ${color};` : "";
    },
});
