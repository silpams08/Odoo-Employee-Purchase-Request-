# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class StockPicking(models.Model):

    _inherit = "stock.picking"

    date_picking = fields.Date('Picking Date')

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        request_id = self.env['purchase.request'].search([('po_id', '=', self.purchase_id.id)])
        if request_id:
            request_id.write({'picking_date': self.date_picking, 'state': 'Ready to pick - up'})
        return res