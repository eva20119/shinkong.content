# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.browser.folder import FolderView
from shinkong.content import _
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from email.mime.text import MIMEText
import json
import datetime


class DebugView(BrowserView):
    def __call__(self):
        request = self.request
        context = self.context
        portal = api.portal.get()
        import pdb; pdb.set_trace()


class SearchProductView(BrowserView):
    template = ViewPageTemplateFile('templates/search_product_view.pt')
    def __call__(self):
        return self.template()


class SearchProductResult(BrowserView):
    template = ViewPageTemplateFile('templates/search_product_result.pt')
    def __call__(self):
        request = self.request
        portal = api.portal.get()

        denier = request.get('denier')
        filament = request.get('filament')
        high_tenacity = request.get('high_tenacity')
        elongation = request.get('elongation')
        has2 = request.get('has2')

        productBrains = api.content.find(context=portal['products'], depth=1, portal_type='product')
        data = {}

        if denier and not filament:
            filamentList = []
            for product in productBrains:
                obj = product.getObject()
                objDenier = obj.denier
                if float(denier) == objDenier:
                    filament = obj.filament
                    filamentList.append(filament)
            return json.dumps(filamentList)
        else:
            filament = float(filament)
            denier = float(denier)
            query = {
                'context': portal['products'],
                'portal_type': 'product', 
                'index_filament' : filament, 
                'index_denier' : denier
            }
            if high_tenacity:
                high_tenacity = float(high_tenacity)
                query['index_ht_min'] = {'query': high_tenacity, 'range': 'max'}
                query['index_ht_max'] = {'query': high_tenacity, 'range': 'min'}
            if has2:
                has2 = float(has2)
                query['index_h2_min'] = {'query': has2, 'range': 'max'}
                query['index_h2_max'] = {'query': has2, 'range': 'min'}
            if elongation:
                elongation = float(elongation)            
                query['index_el_min'] = {'query': elongation, 'range': 'max'}
                query['index_el_max'] = {'query': elongation, 'range': 'min'}
            filterProduct = api.content.find(**query)
            for item in filterProduct:
                obj = item.getObject()
                productUrl = obj.absolute_url()
                productName = obj.title
                data[productName] = productUrl
            self.data = data if data else False
            return self.template()
