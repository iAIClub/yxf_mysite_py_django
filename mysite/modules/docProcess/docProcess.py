#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
import mammoth
import zipfile
import os
import re
import shutil
import chardet
import subprocess
import logging

'''
pandoc不支持直接转换docx文档，先用mammoth把docx转换为html（保留表格），再用pandoc转换为md(markdown_strict保留html原文)
mammoth可选择图片内嵌或存到外部
shell执行mammoth，文件名不能带有&字符（shell本身的问题，特殊符号）
mammoth会改文件名，甚至逗号等一般符号也给改掉（任何英文标点符号都会被删，连中文符号都会被删，太无脑，只能用-）
需要通过正则表达式手动修改图片url，替换为可在线访问的网站链接
'''


# 此函数只执行单个文件，若要执行整个目录则需要在外部循环调用
def execute_docx(fullpath, gen_online=True):
    curPath = os.path.dirname(fullpath)
    filename = fullpath.split('/')[-1].split('.')[0]
    targetPath = './'+curPath+'/'+filename
    file_middle = targetPath+'/'+filename+'.html'
    file_to = targetPath + '/' + filename + '.md'
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    # execute mammoth->html
    p1 = subprocess.Popen('mammoth {0} --output-dir={1}'.format(fullpath,targetPath)
                         , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.wait()
    info = fullpath
    logging.error(info)
    if p1.returncode != 0:
        err1 = p1.stderr.readlines()
        logging.error(err1)
    if gen_online:  # 在线访问版本，图片由公网网站提供
        # change url
        column_slug = curPath.split('/')[-1]
        f1 = open(file_middle, "r")
        content = f1.read()
        f1.close()
        t1 = re.sub(re.compile(r'alt="[\S]*?"'), '', content)
        t2 = re.sub(re.compile(r'src="(?=[0-9]+\.[a-zA-Z]+)'),
                    'src="{0}'.format('/tutorial/doc/'+column_slug+'/'+filename+'/image/'), t1)
        with open(file_middle, "wb") as f2:
            f2.write(t2)
    else:  # 离线访问版本，图片由本地文件提供
        pass
    # execute pandoc->md
    __execute_pandoc(file_middle,file_to)
    # move file to topdir
    shutil.move(file_middle, curPath)
    shutil.move(file_to, curPath)


# 由execute_doc()调用，docx转为html后再调用pandoc转为md
def __execute_pandoc(file_middle,file_to):
    p = subprocess.Popen('pandoc -f html -t markdown_strict {0} -o {1}'.format(file_middle,file_to)
                         , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        err = p.stderr.readlines()
        logging.error(err)
