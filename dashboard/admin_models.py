from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike, BaseSQLAFilter
from wtforms.fields import SelectField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired
from wtforms import validators
from flask_wtf import FlaskForm

from api.models.order import Order
from api.models.user import User
from api.models.restaurant import Restaurant
from api.models.menu import Item, Section
from api.models.order import OrderItem
from flask import current_app, flash
from flask import redirect, url_for, request


class RestaurantModelView(ModelView):
    pass


class UserNameFilter(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.join(User, Order.created_by == User.id).filter(User.name.ilike("%" + value + "%"))

    def operation(self):
        return 'ilike'


class ItemModelView(ModelView):
    column_list = ('title', 'image_url', 'price',
                   'section_id', 'restaurant.cname')

    form_columns = ['title', 'section_id', 'created_by',
                    'modified_by', 'restaurant_id', 'image_url', 'price']

    form_args = {
        'title': {
            'validators': [validators.DataRequired()]
        },
        'price': {
            'validators': [validators.DataRequired()]
        }
    }


class SectionModelView(ModelView):
    column_list = ('title', 'restaurant.cname')

    form_columns = ['title', 'created_by', 'modified_by', 'restaurant_id']

    form_args = {
        'title': {
            'validators': [validators.DataRequired()]
        }
    }

    column_labels = {
        'restaurant.cname': 'Restaurant'
    }


class OrderItemForm(FlaskForm):
    item_id = SelectField('Item', coerce=int)
    quantity = IntegerField('Quantity', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        items = [(item.id, item.title) for item in Item.query.all()]
        self.item_id.choices = items


class OrderAdmin(ModelView):
    column_list = ('id', 'state', 'total_price',
                   'expected_time_arrival', 'user', 'restaurant')
    column_sortable_list = ('created_by', 'restaurant_id',
                            'state', 'expected_time_arrival', 'total_price')
    column_searchable_list = ('created_by', 'restaurant_id')

    column_formatters = {
        'total_price': lambda v, c, m, p: m.total_price(),
        'user': lambda v, c, m, p: m.user.email if m.user else None,
        'restaurant': lambda v, c, m, p: m.restaurant.name if m.restaurant else None,
        'state': lambda v, c, m, p: m.state
    }

    column_filters = ('user.name', 'restaurant.name')

    form_args = {
        'orderitems': {
            'label': 'Order Items'
        }
    }

    def edit_form(self, obj=None):
        form = super(OrderAdmin, self).edit_form(obj)
        self._set_item_choices(form)
        return form

    def create_form(self):
        form = super(OrderAdmin, self).create_form()
        self._set_item_choices(form)

        # Simply load items and flash them for debugging
        try:
            items = [(item.id, item.title) for item in Item.query.all()]
            flash(f'Loaded items: {items}')
        except Exception as e:
            flash(f'Error loading items: {e}')

        return form

    def _set_item_choices(self, form):
        choices = [(item.id, item.title) for item in Item.query.all()]
        for entry_form in form.orderitems:
            entry_form.item_id.choices = choices

    def __init__(self, model, session, **kwargs):
        super(OrderAdmin, self).__init__(model, session, **kwargs)
