#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from saucenao.files.constraint import Constraint
from saucenao.files.filter import Filter

test_dir = 'E:\\Downloads\\temp'
test_files = os.listdir(test_dir)
f = Filter(creation_date=Constraint('01.01.2018 12:28', cmp_func=Constraint.cmp_value_bigger))
filtered_files = f.apply(test_files, test_dir)
for f in filtered_files:
    print(f)
