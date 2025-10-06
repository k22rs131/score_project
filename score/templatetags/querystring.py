# myapp/templatetags/querystring.py
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring(get_params, **kwargs):
    """GETパラメータを保ったまま、任意の値を上書きする"""
    query = get_params.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()
