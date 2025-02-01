import os
from tempfile import mkdtemp

import biocframe
from dolomite_base import read_object, save_object
import dolomite_spatial
import numpy
from spatialexperiment import SpatialExperiment

def test_basic_reader():
    rpath = os.getcwd() + "/tests/data"

    spe = read_object(rpath)
    assert isinstance(spe, SpatialExperiment)

    assert spe.shape == (50, 99)
    assert "sample_id" in spe.get_column_data().get_column_names()
    assert len(set(spe.get_column_data().get_column("sample_id")).difference(["section1", "section2"])) == 0

def test_basic_writer():
    rpath = os.getcwd() + "/tests/data"
    dir = os.path.join(mkdtemp(), "spatial_rtrip")

    spe = read_object(rpath)
    assert isinstance(spe, SpatialExperiment)

    save_object(spe, dir)

    rtrip =  read_object(dir)
    assert isinstance(spe, rtrip)
    assert spe.shape == rtrip.shape
    assert "sample_id" in rtrip.get_column_data().get_column_names()
    assert len(set(rtrip.get_column_data().get_column("sample_id")).difference(["section1", "section2"])) == 0