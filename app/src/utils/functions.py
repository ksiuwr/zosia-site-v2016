# -*- coding: utf-8 -*-
import re


def last_first_name_key(user_name):
    user_name = user_name.lower()
    m = re.match(r"(\w+) (\w+)", user_name)

    return tuple(reversed(m.groups()))
