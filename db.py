#!/usr/bin/env python
# encoding: utf-8


from sqlalchemy import Column, Integer, BigInteger, Numeric, String, Table, MetaData

metadata = MetaData()

t_kline = Table(
    '', metadata,
    Column("open_time", BigInteger, primary_key=True),
    Column("close_time", BigInteger),
    Column("open_price", Numeric(32, 16)),
    Column("close_price", Numeric(32, 16)),
    Column("high_price", Numeric(32, 16)),
    Column("low_price", Numeric(32, 16)),
    Column("base_volumn", Numeric(32, 16)),
    Column("quote_volumn", Numeric(32, 16)),
    Column("trades_count", Integer),
    Column("taker_buy_base_volumn", Numeric(32, 16)),
    Column("taker_buy_quote_volumn", Numeric(32, 16)),
    Column("reserved", String(64))
)
