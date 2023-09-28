#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author      : Ceyhun Uzunoglu <ceyhunuzngl AT gmail [DOT] com>
Description : FastAPI tests
"""

from fastapi import __version__


def test_version(fast_api_client_test):
    response = fast_api_client_test.get("/version")
    assert response.status_code == 200
    msg = str(response.json())
    assert msg == str(__version__)


def test_root_files_size(config_test, create_histograms_for_test, run_size, era_suffixes):
    groups_size = len(config_test.plots.groups)
    assert len(create_histograms_for_test) == groups_size * run_size * len(era_suffixes)
