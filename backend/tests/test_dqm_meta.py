#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author      : Ceyhun Uzunoglu <ceyhunuzngl AT gmail [DOT] com>
Description : DQM meta store tests
"""
import pytest, os
from backend.dqm_meta import eos_grinder
from backend.dqm_meta import client
from backend.dqm_meta.models import *


@pytest.fixture
def eos_grinder_run(config_test):
    # fixture to initialize EOS Grinder run
    eos_grinder.run(config_test)
    yield "I grinded EOS mock directory"
    os.remove(config_test.dqm_meta_store.find_tmp_results_file)
    os.remove(config_test.dqm_meta_store.meta_store_json_file)


@pytest.fixture
def dqm_client(config_test, eos_grinder_run) -> DqmMetaStore:
    # fixture to initialize DMQ METADATA CLIENT which depends on eos_grinder_run
    print(eos_grinder_run)
    dqm_client = client.get_dqm_store(config=config_test)
    return dqm_client


def test_eos_grinder_run(config_test, eos_grinder_run, create_histograms_for_test):
    # run eos_grinder
    print(eos_grinder_run)
    with open(config_test.dqm_meta_store.find_tmp_results_file) as f:
        find_tmp_results_line_cnt = len(f.readlines())

    # Check all root files are parsed by eos_grinder
    assert find_tmp_results_line_cnt == len(create_histograms_for_test)


def test_max_run_number(dqm_client, run_size, era_suffixes, init_run_num, era_run_jump):
    assert dqm_client.get_max_run() == (era_run_jump * (len(era_suffixes) - 1)) + init_run_num + (run_size - 1)


def test_get_meta_by_group_and_run(dqm_client):
    assert dqm_client.get_meta_by_group_and_run("JetMET1", 100000) == DqmMeta(
        dataset="JetMET1/Run2023A-TEST-DATASET",
        eos_directory="JetMET1",
        era="Run2023A",
        root_file="backend/tests/DQMGUI_data/Run2023/JetMET1/0001000xx/DQM_V0001_R000100000__JetMET1__Run2023A-TEST-DATASET__DQMIO.root",
        run=100000,
    )


# TODO write more tests
