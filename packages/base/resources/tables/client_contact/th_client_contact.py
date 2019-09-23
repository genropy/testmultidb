#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('client_id')
        r.fieldcell('name')
        r.fieldcell('phone')

    def th_order(self):
        return 'client_id'

    def th_query(self):
        return dict(column='id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('client_id')
        fb.field('name')
        fb.field('phone')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
