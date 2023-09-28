#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author      : Ceyhun Uzunoglu <ceyhunuzngl AT gmail [DOT] com>
Description : Pytest FastAPI test client initializer
"""
import pathlib, shutil, os
from typing import Any, Generator, List
from datetime import datetime


from ROOT import TFile, TH1F
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import get_config, Config, ConfigPlotsGroup


@pytest.fixture(scope="session")
def config_test() -> Generator[Config, Any, None]:
    """Create modified Config for test"""
    conf = get_config()
    conf.dqm_meta_store.base_dqm_eos_dir = "backend/tests/DQMGUI_data"
    conf.dqm_meta_store.last_n_run_years = 1
    yield conf


@pytest.fixture(scope="session")
def run_size() -> int:
    return 3


@pytest.fixture(scope="session")
def init_run_num() -> int:
    return 100000


@pytest.fixture(scope="session")
def era_run_jump() -> int:
    """ERAs are mostly in different 0001234xx directories, so increase each era run num with 100"""
    return 100


@pytest.fixture(scope="session")
def era_suffixes() -> int:
    return ["A", "B", "C", "D", "E"]


@pytest.fixture(scope="session")
def fast_api_client_test() -> Generator[TestClient, Any, None]:
    """Create a new FastAPI TestClient"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def create_histograms_for_test(config_test, run_size, era_suffixes, init_run_num, era_run_jump) -> List[str]:
    """Create all histograms in plots.yaml for each group and each era.

    To not include another parameter in pytest as "--basetemp", tmp_path_factory is not used
    example eos dir: /eos/cms/store/group/comm_dqm/DQMGUI_data/Run2023/JetMET1/0003707xx/DQM_V0001_R000370717__JetMET1__Run2023D-PromptReco-v2__DQMIO.root
    """
    all_created_files = []
    # Mock up the base DQM EOS dirctory for root files
    year = datetime.now().year
    base_directory = pathlib.Path(config_test.dqm_meta_store.base_dqm_eos_dir) / f"Run{year}"

    root_file_fmt = "DQM_V0001_R{run9d}__{eosdir}__{era}-TEST-DATASET__DQMIO.root"
    eras = [f"Run{year}{e}" for e in era_suffixes]  # eras full name, i.e. Run2023A

    # Iterare all groups and creates all histograms defined in plots.yaml in each era
    for group_conf in config_test.plots.groups:
        # Each group will have same histograms of same numbers
        first_run = init_run_num  # First Run number with 6 digit, max Run digit is 9

        group_dir = base_directory / group_conf.eos_directory

        for era in eras:
            for run in range(first_run, first_run + run_size):
                run_xx_dir = group_dir / f"{str(int(first_run / 100))}xx".zfill(9)
                run_xx_dir.mkdir(parents=True, exist_ok=True)

                # Create all plots of the group in the ROOT file
                root_f = run_xx_dir / root_file_fmt.format(
                    run9d=str(run).zfill(9), eosdir=group_conf.eos_directory, era=era
                )
                util_create_root_hist(root_file=str(root_f), group_conf=group_conf, run=run)
                all_created_files.append(root_f)
            first_run += era_run_jump  # to change run_xx directory which depends on last 2 digit of the run number

    yield all_created_files
    # Delete after session
    # ATTENTION: YOU CAN USE FOR DEVELOPMENT TOO SO COMMENT OUT DELETION TO SEE HISTS
    shutil.rmtree(base_directory.parent)  # DQMGUI_data is parent


def util_create_root_hist(root_file: str, group_conf: ConfigPlotsGroup, run: int):
    """Creates test histograms in th root file with the definitions in plots.yaml config only for TH1F

    PYROOT has limited functionalities to create object sub directory and iterate it. That's why, iterating all
    the sub directories and creating them, writing test plot to that directory is only possible with this way.
    """
    tdirectory = group_conf.tdirectory.format(run_num_int=run)
    tdirectory_subdir_list = tdirectory.split("/")
    plot_dirs = sorted(set([p.name for p in group_conf.plots]))  # Their directories can be same, so get set
    plot_subdir_list = [p_dir.split("/")[:-1] for p_dir in plot_dirs]  # Only directories, no name

    with TFile(root_file, "UPDATE") as tf:
        # === Create tdirectory subdirs first

        # It is the child directory of tdirectory: "Run Summary" mostly
        pivot_main_dir = tf.mkdir(tdirectory_subdir_list[0])
        for d in tdirectory_subdir_list[1:]:  # skip first parent dir which is already created
            pivot_main_dir = pivot_main_dir.mkdir(d)

        # === Create sub directories of histograms which come in their name actually
        for plot_subdirs in plot_subdir_list:
            pivot_plot_dir = pivot_main_dir  # start from the child directory of tdirectory
            for d in plot_subdirs:  # Iterate pivot subdirs and create if not exist
                if not pivot_plot_dir.GetDirectory(d):
                    pivot_plot_dir = pivot_plot_dir.mkdir(d)
                else:
                    pivot_plot_dir = pivot_plot_dir.GetDirectory(d)

        # === It's certain that all subdirectories are created in the previous steps,
        #     so let's get childe Directory object and write hist there
        for plot_conf in group_conf.plots:
            plot_dir = "/".join(plot_conf.name.split("/")[:-1])  # before last
            name = plot_conf.name.split("/")[-1]  # last
            root_plot_dir = pivot_main_dir.GetDirectory(plot_dir)
            # Create histogram and write to child directory
            __h = TH1F(name, name, 64, -4, 4)
            __h.FillRandom("gaus")
            root_plot_dir.WriteObject(__h, name)
            del __h
