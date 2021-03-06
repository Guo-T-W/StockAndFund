#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 29/06/2020 00:38
# @Author  : Ziye Yang
# @Purpose : To select best fund base on TuShare's dataset

import logging
import pickle
import time

import tushare as ts
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Fund:
    def __init__(self, on_market_time):
        """

        Args:
            on_market_time: choose funds which has on market time longer than this
        """
        self.on_market_time = on_market_time
        self.tushare = ts.pro_api('b73a6d783f9f180f97d2810a73338f22abd3cd5eea289587d6860749')
        self.fund_info = {}
        self.request_net_value_times = 0
        self.get_active_funds()

    def get_active_funds(self):
        """
        get all active fund with on market days > requested days

        """
        df = self.tushare.fund_basic(status='L')
        logger.info("found {} active funds".format(len(df)))
        for code in tqdm(df['ts_code'].tolist()):
            net_value, net_value_date = self.get_net_values(code)
            if net_value is not None:
                index = df.index[df['ts_code'] == code]
                self.fund_info[code] = {}
                self.fund_info[code]['net_value'] = net_value
                self.fund_info[code]['net_value_date'] = net_value_date
                self.fund_info[code]['fund_type'] = df['fund_type'][index].tolist()[0]
                self.fund_info[code]['management'] = df['management'][index].tolist()[0]
                self.fund_info[code]['m_fee'] = df['m_fee'][index].tolist()[0]
                self.fund_info[code]['c_fee'] = df['c_fee'][index].tolist()[0]

        date = time.strftime("%Y%m%d")
        with open(date + '.pkl', 'wb') as output:
            pickle.dump(self.fund_info, output)

    def get_net_values(self, code):
        """
        get adjusted net value of requested fund

        Args:
            code: fund code

        Returns:
            the adjusted net values with dates of this fund as 2 list
        """
        self.request_net_value_times += 1
        if self.request_net_value_times % 100 == 0:
            print("wait for 10s")
            time.sleep(10)

        df = self.tushare.fund_nav(ts_code=code)
        on_market_time = len(df.values)
        if on_market_time > self.on_market_time and self.check_is_valid_fund(df['adj_nav'].tolist()):
            return df['adj_nav'].tolist(), df['end_date'].tolist()
        else:
            return None, None

    @staticmethod
    def check_is_valid_fund(net_values):
        """

        Args:
            net_values: net values of fund as a list

        """
        # not valid if all element of net values are the same
        if net_values.count(net_values[0]) == len(net_values):
            return False
        return True


if __name__ == "__main__":
    Fund = Fund(365)
