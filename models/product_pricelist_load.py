
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 15/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, exceptions, api, _


class ProductPricelistLoad(models.Model):
    _name = 'product.pricelist.load'
    _description = 'Product Price List Load'

    name = fields.Char('Load')
    date = fields.Date('Date:', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    file_lines = fields.One2many('product.pricelist.load.line', 'file_load',
                                 'Product Price List Lines')
    fails = fields.Integer('Fail Lines:', readonly=True)
    process = fields.Integer('Lines to Process:', readonly=True)
    supplier = fields.Many2one('res.partner')

    @api.multi
    def process_lines(self):
        for file_load in self:
            if not file_load.supplier:
                raise exceptions.Warning(_("You must select a Supplier"))
            product_obj = self.env['product.product']
            psupplinfo_obj = self.env['product.supplierinfo']
            pricepinfo_obj = self.env['pricelist.partnerinfo']
            if not file_load.file_lines:
                raise exceptions.Warning(_("There must be one line at least to"
                                           " process"))
            for line in file_load.file_lines:
                # process fail lines
                if line.fail:
                    # search product sku
                    if line.sku:
                        product_lst = product_obj.search([('default_code', '=',
                                                           line.sku)])
                        if product_lst:

			    existing_supplier_ids = psupplinfo_obj.search(cr, uid, [\
				('name', '=', file_load.supplier.id),
				('product_tmpl_id', '=', product_lst[0].product_tmpl_id.id)
			    ])

			    if existing_supplier_ids:
				psupplinfo_id = existing_supplier_ids[0]
				psupplinfo = psupplinfo_obj.create.browse(cr, uid, psupplinfo_id)
			    else:
                                psupplinfo = psupplinfo_obj.create(
                                    {'name': file_load.supplier.id,
                                     'product_tmpl_id': \
                                     product_lst[0].product_tmpl_id.id})


			    vals1 = self.prepare_price_dict(self, line, psupplinfo, 'initial')
			    self.process_price_dict(line, vals1)

			    if line.pricebreak_two:
				print 'Processing line 2'
				vals2 = self.prepare_price_dict(self, line, psupplinfo, 'second')

			    if line.pricebreak_three:
				print 'Processing line 3'
				vals3 = self.prepare_price_dict(self, line, psupplinfo, 'third')

                            file_load.fails -= 1
                            line.write(
                                {'fail': False,
                                 'fail_reason': _('Correctly Processed')})
                        else:
                            line.fail_reason = _('Product not found')
        return True


    def process_price_dict(self, line, vals):
	uid = 1
	cr = self.cr

	pricepinfo_obj = self.pool.get('pricelist.partnerinfo')
	existing_ids = pricepinfo_obj.search(cr, uid, [\
		('min_quantity', '=', vals['min_quantity),
		('suppinfo_id', '=' vals['suppinfo_id']),
		('price', '=', vals['price'])
	])

	if existing_ids:
	    pass

	else:
	    pricepinfo_obj.create(cr, uid, vals)
		
	return True


    def prepare_price_dict(self, line, supplierinfo_id):
	d = {
	    'suppinfo_id': supplierinfo_id	    
	}

	if t == 'initial':
	    d['min_quantity'] = 0
	    d['price'] = line.price
	elif t == 'second':
	    d['min_quantity'] = line.qty_2
	    d['price'] = line.price_2
	elif t == 'third':
	    d['min_quantity'] = line.qty_3
	    d['price'] = line.price_3

	return d


class ProductPricelistLoadLine(models.Model):
    _name = 'product.pricelist.load.line'
    _description = 'Product Price List Load Line'

    sku = fields.Char('Product SKU', required=True)
    description = fields.Char('Product Description')
    vendor_sku = fields.Char('Vendor Sku')
    price = fields.Float('Product Price', required=True)
    price_2 = fields.Float('Price 2')
    price_3 = fields.Float('Price 3')
    qty_2 = fields.Float('Price Break Qty 2')
    qty_3 = fields.Float('Price Break Qty 3')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load = fields.Many2one('product.pricelist.load', 'Load',
                                required=True)
