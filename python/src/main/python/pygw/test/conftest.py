#
# Copyright (c) 2013-2020 Contributors to the Eclipse Foundation

#
# See the NOTICE file distributed with this work for additional information regarding copyright
# ownership. All rights reserved. This program and the accompanying materials are made available
# under the terms of the Apache License, Version 2.0 which accompanies this distribution and is
# available at http://www.apache.org/licenses/LICENSE-2.0.txt
# ===============================================================================================

import pytest
import os
import shutil
import time

from datetime import datetime

from shapely.geometry import Point

from pygw.store import DataStoreFactory
from pygw.store.rocksdb import RocksDBOptions
from pygw.geotools import SimpleFeatureTypeBuilder
from pygw.geotools import AttributeDescriptor
from pygw.geotools import FeatureDataAdapter
from pygw.geotools import SimpleFeatureBuilder

# "Point" Type
POINT_TYPE_NAME = "TestPointType"
POINT_GEOMETRY_FIELD = "the_geom"
POINT_TIME_FIELD = "date"
POINT_NUMBER_FIELD = "flt"
_point_type_builder = SimpleFeatureTypeBuilder()
_point_type_builder.set_name(POINT_TYPE_NAME)
_point_type_builder.add(AttributeDescriptor.point(POINT_GEOMETRY_FIELD))
_point_type_builder.add(AttributeDescriptor.date(POINT_TIME_FIELD))
_point_type_builder.add(AttributeDescriptor.float(POINT_NUMBER_FIELD))
POINT_TYPE = _point_type_builder.build_feature_type()

# "Point" Type Adapter
POINT_TYPE_ADAPTER = FeatureDataAdapter(POINT_TYPE)

# "Point" Feature builder
POINT_FEATURE_BUILDER = SimpleFeatureBuilder(POINT_TYPE)


def _create_feature(fid, geometry, timestamp):
    POINT_FEATURE_BUILDER.set_attr(POINT_GEOMETRY_FIELD, geometry)
    POINT_FEATURE_BUILDER.set_attr(POINT_TIME_FIELD, datetime.utcfromtimestamp(timestamp))
    POINT_FEATURE_BUILDER.set_attr(POINT_NUMBER_FIELD, timestamp)
    return POINT_FEATURE_BUILDER.build(fid)


TEST_DATA = [
    _create_feature(id_, Point(i, j), i) for
    id_, (i, j) in enumerate(zip(range(-180, 180), range(-180, 180)))]

# Test Directory
TEST_DIR = os.path.join(os.getcwd(), "test")


@pytest.fixture
def test_ds():
    os.makedirs(TEST_DIR, exist_ok=True)
    options = RocksDBOptions()
    options.set_geowave_namespace("geowave.tests")
    options.set_directory(os.path.join(TEST_DIR, "datastore"))
    ds = DataStoreFactory.create_data_store(options)
    yield ds
    # teardown here
    ds.delete_all()
    shutil.rmtree(TEST_DIR)
    while os.path.isdir(TEST_DIR):
        time.sleep(0.01)


def write_test_data(ds, *expected_indices):
    writer = ds.create_writer(POINT_TYPE_ADAPTER.get_type_name())
    for pt in TEST_DATA:
        results = writer.write(pt)
        assert not results.is_empty()
        written_indices = results.get_written_index_names()
        assert len(written_indices) == len(expected_indices)
        assert all([idx.get_name() in written_indices for idx in expected_indices])
    writer.close()


def results_as_list(results):
    res = [d for d in results]
    results.close()
    return res
