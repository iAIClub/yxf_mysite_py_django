#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import mammoth
import zipfile
import os
import shutil
import chardet
import logging

'''
pandoc并不好用，首先就是不支持直接转换docx文档，所以弃用
使用mammoth，可以把docx转换为原始的html或者是md，且html的图片是内嵌的
'''


# 在windows下压缩到linux解压存在文件名编码问题（gb2312->utf-8），通过以下代码解决
def unzip(filepath,filename):
    with zipfile.ZipFile(filepath+filename, 'r') as f:
        for name in f.namelist():  # 递归获取压缩包内所有的文件或目录名（具有相对压缩包位置的完整路径）
            origin_encoding = chardet.detect(name)
            utf8name = filepath+name.decode(origin_encoding['encoding'])  # 获得解码后的正确名称
            pathname = os.path.dirname(utf8name)
            if not os.path.exists(pathname) and pathname != "":
                os.makedirs(pathname)
            data = f.read(name)  # 直接从压缩包中读取文件，不经过解压过程（解压过程不支持中文的bug）
            if not os.path.exists(utf8name):
                fo = open(utf8name, "w")
                fo.write(data)
                fo.close()


# 此函数只执行单个文件，若要执行整个目录则需要在外部循环调用
def execute_doc(file_from,do_html=True):
    curPath = os.path.dirname(file_from)
    filename = file_from.split('/')[-1].split('.')[0]
    targetPath = curPath
    file_middle = targetPath + os.path.sep + filename + '.html'
    file_to = targetPath + os.path.sep + filename + '.md'
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    with open(file_from, "rb") as docx_file:
        md = mammoth.convert_to_markdown(docx_file)
        with open(file_to, "w") as f:
            f.write(md.value)
    if do_html:
        with open(file_from, "rb") as docx_file:
            html = mammoth.convert_to_html(docx_file)
            with open(file_middle, "w") as f:
                f.write(html.value)
