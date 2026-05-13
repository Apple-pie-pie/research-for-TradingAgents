"""Config isolation: get/set must not leak nested-dict references."""

import copy
import unittest
from unittest.mock import patch

import pytest
from yfinance.exceptions import YFRateLimitError

import tradingagents.default_config as default_config
from tradingagents.dataflows.config import get_config, set_config
from tradingagents.dataflows.interface import route_to_vendor


@pytest.mark.unit
class DataflowsConfigIsolationTests(unittest.TestCase):
    def setUp(self):
        set_config(copy.deepcopy(default_config.DEFAULT_CONFIG))

    def test_get_config_returns_deep_copy(self):
        cfg = get_config()
        cfg["data_vendors"]["core_stock_apis"] = "alpha_vantage"
        cfg["tool_vendors"]["get_stock_data"] = "alpha_vantage"

        fresh = get_config()
        self.assertEqual(
            fresh["data_vendors"]["core_stock_apis"],
            default_config.DEFAULT_CONFIG["data_vendors"]["core_stock_apis"],
        )
        self.assertEqual(
            fresh["tool_vendors"],
            default_config.DEFAULT_CONFIG["tool_vendors"],
        )

    def test_set_config_does_not_alias_caller_nested_dicts(self):
        custom = copy.deepcopy(default_config.DEFAULT_CONFIG)
        custom["data_vendors"]["core_stock_apis"] = "alpha_vantage"
        custom["tool_vendors"]["get_stock_data"] = "alpha_vantage"

        set_config(custom)

        custom["data_vendors"]["core_stock_apis"] = "yfinance"
        custom["tool_vendors"]["get_stock_data"] = "yfinance"

        fresh = get_config()
        self.assertEqual(fresh["data_vendors"]["core_stock_apis"], "alpha_vantage")
        self.assertEqual(fresh["tool_vendors"]["get_stock_data"], "alpha_vantage")

    def test_partial_nested_update_preserves_existing_defaults(self):
        set_config(
            {
                "data_vendors": {
                    "core_stock_apis": "alpha_vantage",
                }
            }
        )

        fresh = get_config()
        self.assertEqual(fresh["data_vendors"]["core_stock_apis"], "alpha_vantage")
        self.assertEqual(
            fresh["data_vendors"]["technical_indicators"],
            default_config.DEFAULT_CONFIG["data_vendors"]["technical_indicators"],
        )
        self.assertEqual(
            fresh["data_vendors"]["fundamental_data"],
            default_config.DEFAULT_CONFIG["data_vendors"]["fundamental_data"],
        )
        self.assertEqual(
            fresh["data_vendors"]["news_data"],
            default_config.DEFAULT_CONFIG["data_vendors"]["news_data"],
        )

    def test_nested_dict_updates_merge_one_level_deep(self):
        set_config({"tool_vendors": {"get_stock_data": "alpha_vantage"}})
        set_config({"tool_vendors": {"get_news": "alpha_vantage"}})

        fresh = get_config()
        self.assertEqual(fresh["tool_vendors"]["get_stock_data"], "alpha_vantage")
        self.assertEqual(fresh["tool_vendors"]["get_news"], "alpha_vantage")

    def test_yfinance_rate_limit_falls_back_to_next_vendor(self):
        set_config({"tool_vendors": {"get_stock_data": "yfinance,alpha_vantage"}})

        with patch(
            "tradingagents.dataflows.interface.get_YFin_data_online",
            side_effect=YFRateLimitError(),
        ), patch(
            "tradingagents.dataflows.interface.get_alpha_vantage_stock",
            return_value="timestamp,open\n2026-05-13,1.0\n",
        ):
            from tradingagents.dataflows import interface as interface_module

            original_methods = interface_module.VENDOR_METHODS["get_stock_data"]
            interface_module.VENDOR_METHODS["get_stock_data"] = {
                "yfinance": interface_module.get_YFin_data_online,
                "alpha_vantage": interface_module.get_alpha_vantage_stock,
            }
            try:
                result = route_to_vendor("get_stock_data", "TSLA", "2026-05-01", "2026-05-13")
            finally:
                interface_module.VENDOR_METHODS["get_stock_data"] = original_methods

        self.assertIn("timestamp,open", result)
