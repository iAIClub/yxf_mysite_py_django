#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function,unicode_literals,division
import random


'''
代码参考:https://www.jianshu.com/p/b92d791ad008,木子昭
'''


def bucket_sort(unsort_list):
    '''
    桶排序:
    将列表中最大数与最小数之间的数全部做成标签,贴到N个桶上
    将每个元素放到对应值的桶里面(如果有M个相同的元素值,则将M个元素全部放到相应的桶中,取的时候占用M个位置)
    最后按照桶编号的先后顺序,从桶中依次取出值,排列完成
    '''
    # create bucket
    max_data = max(unsort_list)
    min_data = min(unsort_list)
    bucket_list = []
    for i in range(min_data,max_data+1):
        bucket_list.append([i,0])

    # mapping data to bucket
    for data in unsort_list:
        for bucket in bucket_list:
            if bucket[0] == data:
                bucket[1] += 1

    # return
    result = []
    for bucket in bucket_list:
        for data in range(0,bucket[1]):
            result.append(bucket[0])
    return result


def bubble_sort(unsort_list):
    '''
    冒泡排序:
    有N个待排序元素
    1.设置游标,游标带领第一个元素开始,与右侧元素(第1个元素)比较,如果大于右侧元素,则二者交换数值,然后游标带领元素继续向右移动，如果小于右侧元素,则不进行交换，游标继续向右移动，当游标移动到列表最右侧，第一轮比较就完成了（共比较N-1次）
    2.然后游标回到起始位置，开始第二轮比较，由于最后一个元素已经确定大于剩余的元素所以(第二轮共比较N-2)次。
    3.由于每次都只能选取出一个最大值,所以N个元素的数组,进行N-1轮对比即可完成排列
    '''
    pass


def select_sort(unsort_list):
    '''
    选择排序:
    首先在未排序序列中找到最小（大）元素，存放到排序序列的起始位置，然后，再从剩余未排序元素中继续寻找最小（大）元素，然后放到已排序序列的末尾。以此类推，直到所有元素均排序完毕。
    '''
    pass


def insert_sort(unsort_list):
    '''
    插入排序:
    序列共有N个元素
    将序列分为,已排序序列(第一个元素) 和 未排序序列(除第一个元素以外的其它元素，共N-1个）两部分,然后通过N-1轮循环,将N-1个元素,依次添加到已排序序列中
    '''
    pass


def quick_sort(unsort_list):
    '''
    快速排序
    1.选择左侧第一个元素为 基准元素(其实基准元素可以是任意值,这里选择第一个是为了方便叙述)
    '''
    pass


def shell_sort(unsort_list):
    '''
    希尔排序:
    希尔排序是为优化插入排序,而创建的算法, 其核心思想是通过设置步长 将元素分组，对每个分组进行快速排序,然后将步长减少,产生新的分组，对每个新分组进行快速排序，当步长减为1时,完成排序
    '''
    pass


def merge_sort(unsort_list):
    '''
    归并排序(python内置sort方法的实现原理):
    归并排序是典型的分治法排序，将待排序元素拆成多个分组，分组内部进行排序，然后分组进行合并，最终合并成完整的数组。
    '''
    pass


if __name__ == '__main__':
    # data
    unsort_list = []
    for i in range(0,10):
        unsort_list.append(random.randint(10,99))
    print('原始未排序序列：',unsort_list)
    # sort algorithm
    bucket_sort_res = bucket_sort(unsort_list)
    print('桶排序结果：',bucket_sort_res)
