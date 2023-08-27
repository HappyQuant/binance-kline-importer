#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import glob
import json
import decimal
from enum import Enum

from dotenv import load_dotenv
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session

from db import t_kline


class KLineSymbol(Enum):
    BtcUsdt = "BTCUSDT"
    EthUsdt = "ETHUSDT"


class KLineInterval(Enum):
    OneMinute = "1m"
    ThreeMinute = "3m"
    FiveMinute = "5m"
    FifteenMinute = "15m"
    ThirtyMinute = "30m"
    OneHour = "1h"
    TwoHour = "2h"
    FourHour = "4h"
    SixHour = "6h"
    EightHour = "8h"
    TwelveHour = "12h"
    OneDay = "1d"


load_dotenv()
db_dsn = os.environ.get("DB_DSN")
engine = create_engine(db_dsn)
db_session = Session(autocommit=False, autoflush=False, bind=engine)

data_dir = "data"
kline_symbol = KLineSymbol.EthUsdt
kline_interval = KLineInterval.OneMinute
data_path = "{}/{}/{}".format(data_dir, kline_symbol.value, kline_interval.value)
if not os.path.exists(data_path):
    print(data_path, "not exist")
    sys.exit(255)

t_kline.name = "t_kline_{}_{}".format(kline_symbol.value, kline_interval.value)
if not engine.dialect.has_table(engine.connect(), t_kline.name):
    t_kline.create(engine)

files = sorted(filter(lambda x: x not in (".", ".."), glob.glob("{}/*".format(data_path))))
for file in files:
    r = open(file, "r")
    klines = json.loads(r.read())
    if len(klines) == 0:
        continue

    results = db_session.query(t_kline).filter(t_kline.c.open_time == klines[0][0]).all()
    if len(results) != 0:
        print("kline data", file, "imported before, skip")
        continue

    db_session.execute(
        insert(t_kline),
        [
            {
                "open_time": kline[0],
                "close_time": kline[6],
                "open_price": decimal.Decimal(kline[1]),
                "close_price": decimal.Decimal(kline[2]),
                "high_price": decimal.Decimal(kline[3]),
                "low_price": decimal.Decimal(kline[4]),
                "base_volume": decimal.Decimal(kline[5]),
                "quote_volume": decimal.Decimal(kline[7]),
                "trades_count": kline[8],
                "taker_buy_base_volume": decimal.Decimal(kline[9]),
                "taker_buy_quote_volume": decimal.Decimal(kline[10]),
                "reserved": kline[11],
            }
            for kline in klines
        ]
    )
    try:
        db_session.commit()
        print("import kline data", file)
    except Exception as ex:
        db_session.rollback()
        print(ex)
        sys.exit(255)
