#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartFetch 智能抓取模块
"""

from .multi_strategy import MultiStrategyFetcher, CookiePool, get_fetcher, get_cookie_pool

__all__ = ["MultiStrategyFetcher", "CookiePool", "get_fetcher", "get_cookie_pool"]
