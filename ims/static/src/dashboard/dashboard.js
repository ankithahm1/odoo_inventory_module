/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SmartDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            moDraft: 0,
            moInProgress: 0,
            moLate: 0,
            poDraft: 0,
            poToApprove: 0,
            poApproved: 0,
            lowStock: [],
            deliveryWaiting: 0,
            deliveryDone: 0,
            deliveryLate: 0,
        });

        this.replenishProduct = this.replenishProduct.bind(this);
        this.openMOView = this.openMOView.bind(this);
        this.openPOView = this.openPOView.bind(this);
        this.openDeliveryView = this.openDeliveryView.bind(this);

        onWillStart(async () => {


            const [
                moDraft, moInProgress, moLate,
                poDraft, poToApprove, poApproved,
                orderpoints,
                deliveryWaiting, deliveryDone, deliveryLate
            ] = await Promise.all([
                this.orm.call("mrp.production", "search_count", [[["state", "=", "draft"]]]),
                this.orm.call("mrp.production", "search_count", [[["state", "=", "progress"]]]),
                this.orm.call("mrp.production", "search_count", [[
                    ["state", "in", ["confirmed", "progress"]],
                    ["date_deadline", "<", new Date()]
                ]]),
                this.orm.call("purchase.order", "search_count", [[["state", "=", "draft"]]]),
                this.orm.call("purchase.order", "search_count", [[["state", "=", "to approve"]]]),
                this.orm.call("purchase.order", "search_count", [[["state", "=", "purchase"]]]),
                this.orm.searchRead("stock.warehouse.orderpoint", [], ["id", "product_id", "product_min_qty"]),
                this.orm.call("stock.picking", "search_count", [[["picking_type_code", "=", "outgoing"], ["state", "=", "confirmed"]]]),
                this.orm.call("stock.picking", "search_count", [[["picking_type_code", "=", "outgoing"], ["state", "=", "done"]]]),
                this.orm.call("stock.picking", "search_count", [[
                    ["picking_type_code", "=", "outgoing"],
                    ["scheduled_date", "<", new Date()],
                    ["state", "in", ["assigned", "confirmed"]]
                ]]),
            ]);

            // Low stock check
            const productIds = orderpoints.map(op => op.product_id?.[0]).filter(Boolean);
            const products = await this.orm.searchRead("product.product", [["id", "in", productIds]], ["id", "display_name", "qty_available"]);
            const productMap = Object.fromEntries(products.map(p => [p.id, p]));
            const lowStock = orderpoints.map(op => {
                const product = productMap[op.product_id?.[0]];
                return {
                    id: op.id,
                    product_min_qty: op.product_min_qty,
                    product: product,
                };
            }).filter(entry => entry.product && entry.product.qty_available < entry.product_min_qty);

            // Update state
            Object.assign(this.state, {
                moDraft, moInProgress, moLate,
                poDraft, poToApprove, poApproved,
                lowStock,
                deliveryWaiting, deliveryDone, deliveryLate,
            });
        });
    }



    openMOView(domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Manufacturing Orders",
            res_model: "mrp.production",
            view_mode: "list,form",
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
        });
    }

    openPOView(domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Purchase Orders",
            res_model: "purchase.order",
            view_mode: "list,form",
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
        });
    }

    openDeliveryView(domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Outgoing Deliveries",
            res_model: "stock.picking",
            view_mode: "list,form",
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
        });
    }

    replenishProduct(productId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Replenishment",
            res_model: "stock.warehouse.orderpoint",
            view_mode: "list,form",
            views: [[false, 'list'], [false, 'form']],
            domain: [["product_id", "=", productId]],
        });
    }
}

// Link template and register component
SmartDashboard.template = "inventory__mrp.SmartDashboardTemplate";
registry.category("actions").add("smart_inv_mrp_dashboard_tag", SmartDashboard);
