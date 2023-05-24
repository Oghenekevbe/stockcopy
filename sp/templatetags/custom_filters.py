from django import template
from ..custom_filters import base64_encode

register = template.Library()
register.filter('base64_encode', base64_encode)

