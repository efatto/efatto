import {QtyAtDateWidget} from "@sale_stock/widgets/qty_at_date_widget";
import {patch} from "@web/core/utils/patch";

patch(QtyAtDateWidget.prototype, {
    initCalcData() {
        super.initCalcData();
        const data = this.props.record.data;
        if (data.is_mto || data.is_kits) {
            this.calcData.forecasted_issue = false;
            return;
        }
        this.calcData.forecasted_issue = Boolean(
            data.virtual_available_at_date < data.qty_to_deliver &&
                data.scheduled_date &&
                data.commitment_date &&
                data.scheduled_date > data.commitment_date
        );
    },
});
