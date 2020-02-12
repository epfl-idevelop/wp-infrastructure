#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour tester la récupération des arguments en python

import sys

for arg in sys.argv:
    print arg

#print("arg1:" + sys.argv[1])
print("len off sys.argv:" , len(sys.argv))
print("sys.argv:" , sys.argv)
