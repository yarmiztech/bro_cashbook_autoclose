# -*- coding: utf-8 -*-
{
    'name': 'Brothers CashBook Auto close',
    'version': '14.0',
    'summary': 'Estimate',
    'author':
        'ENZAPPS',
    'sequence': 20,
    'description': """Brothers CashBook Auto close Every Day""",
    'category': '',
    'website': 'https://enzapps.com',
    'depends': ['base', 'contacts','account','ezp_estimate','enz_multi_updations','enz_mc_owner'],
    'images': ['static/description/logo.png'],
    'data': [
        "data/schedule.xml",
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
