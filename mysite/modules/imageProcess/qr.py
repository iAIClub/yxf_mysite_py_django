#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from io import BytesIO
import qrcode


def getQrcode(text):
    image = qrcode.make(text)
    image_data = BytesIO()
    image.save(image_data, 'jpeg')
    return image_data.getvalue()
