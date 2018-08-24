"""Miscellaneous helper functions"""

import re
# Taken from http://stackoverflow.com/a/1176023
def camelcase_to_snakecase(name_camel):
    name_tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name_camel)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name_tmp).lower()
