# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from itertools import chain

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from shuup.front.utils.sorts_and_filters import ProductListFormModifier


class FilterWidget(forms.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        choices_to_render = []
        for option_value, option_label in chain(self.choices, choices):
            choices_to_render.append((option_value, option_label))
        return mark_safe(
            render_to_string("shuup/front/product/filter_choice.jinja", {
                "name": name, "values": value, "choices": choices_to_render})
        )


class SimpleProductListModifier(ProductListFormModifier):
    is_active_key = ""
    is_active_label = ""
    ordering_key = ""
    ordering_label = ""

    def should_use(self, configuration):
        if not configuration:
            return
        return bool(configuration.get(self.is_active_key))

    def get_ordering(self, configuration):
        if not configuration:
            return 1
        return configuration.get(self.ordering_key, 1)

    def get_admin_fields(self):
        return [
            (self.is_active_key, forms.BooleanField(label=self.is_active_label, required=False)),
            (self.ordering_key, forms.IntegerField(label=self.ordering_label, initial=1))
        ]


class SortProductListByName(SimpleProductListModifier):
    is_active_key = "sort_products_by_name"
    is_active_label = _("Sort products by name")
    ordering_key = "sort_products_by_name_ordering"
    ordering_label = _("Ordering for sort by name")

    def get_fields(self, request, category=None):
        return [("sort", forms.CharField(required=False, widget=forms.Select(), label=_('Sort')))]

    def get_choices_for_fields(self):
        return [
            ("sort", [
                ("name_a", _("Name - A-Z")),
                ("name_d", _("Name - Z-A")),
            ]),
        ]

    def sort_products(self, request, products, data):
        sort = data.get("sort", "name_a")

        def _get_product_name_lowered_stripped(product):
            return product.name.lower().strip()

        if not sort:
            sort = ""

        key = (sort[:-2] if sort.endswith(('_a', '_d')) else sort)
        if key == "name":
            sorter = _get_product_name_lowered_stripped
            reverse = bool(sort.endswith('_d'))
            products = sorted(products, key=sorter, reverse=reverse)
        return products


class SortProductListByCreatedDate(SimpleProductListModifier):
    is_active_key = "sort_products_by_date_created"
    is_active_label = _("Sort products by date created")
    ordering_key = "sort_products_by_date_created_ordering"
    ordering_label = _("Ordering for sort by date created")

    def get_fields(self, request, category=None):
        return [("sort", forms.CharField(required=False, widget=forms.Select(), label=_('Sort')))]

    def get_choices_for_fields(self):
        return [
            ("sort", [
                ("created_date_d", _("Date created")),
            ]),
        ]

    def sort_products(self, request, products, data):
        sort = data.get("sort")

        def _get_product_created_on_datetime(product):
            return product.created_on

        if not sort:
            sort = ""

        key = (sort[:-2] if sort.endswith(('_a', '_d')) else sort)
        if key == "created_date":
            sorter = _get_product_created_on_datetime
            reverse = bool(sort.endswith('_d'))
            products = sorted(products, key=sorter, reverse=reverse)
        return products
