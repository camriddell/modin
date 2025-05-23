# Licensed to Modin Development Team under one or more contributor license agreements.
# See the NOTICE file distributed with this work for additional information regarding
# copyright ownership.  The Modin Development Team licenses this file to you under the
# Apache License, Version 2.0 (the "License"); you may not use this file except in
# compliance with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import copy

import pytest

import modin.pandas as pd
from modin.config import Backend, Engine, Execution, StorageFormat
from modin.core.execution.dispatching.factories import factories
from modin.core.execution.dispatching.factories.factories import BaseFactory, NativeIO
from modin.core.storage_formats.pandas.native_query_compiler import NativeQueryCompiler


class Test1QueryCompiler(NativeQueryCompiler):
    storage_format = property(lambda self: "Test1_Storage_Format")
    engine = property(lambda self: "Test1_Engine")


class Test1IO(NativeIO):
    query_compiler_cls = Test1QueryCompiler


class Test1Factory(BaseFactory):

    @classmethod
    def prepare(cls):
        cls.io_cls = Test1IO


@pytest.fixture(autouse=True)
def clean_up_extensions():

    original_dataframe_extensions = copy.deepcopy(pd.dataframe._DATAFRAME_EXTENSIONS_)
    original_series_extensions = copy.deepcopy(pd.series._SERIES_EXTENSIONS_)
    original_base_extensions = copy.deepcopy(pd.base._BASE_EXTENSIONS)
    yield
    pd.dataframe._DATAFRAME_EXTENSIONS_.clear()
    pd.dataframe._DATAFRAME_EXTENSIONS_.update(original_dataframe_extensions)
    pd.series._SERIES_EXTENSIONS_.clear()
    pd.series._SERIES_EXTENSIONS_.update(original_series_extensions)
    pd.base._BASE_EXTENSIONS.clear()
    pd.base._BASE_EXTENSIONS.update(original_base_extensions)

    from modin.pandas.api.extensions.extensions import _attrs_to_delete_on_test

    for k, v in _attrs_to_delete_on_test.items():
        for obj in v:
            delattr(k, obj)
    _attrs_to_delete_on_test.clear()


@pytest.fixture
def Backend1():
    factories.Test1_Storage_FormatOnTest1_EngineFactory = Test1Factory
    if "Backend1" not in Backend.choices:
        StorageFormat.add_option("Test1_storage_format")
        Engine.add_option("Test1_engine")
        Backend.register_backend(
            "Backend1",
            Execution(storage_format="Test1_Storage_Format", engine="Test1_Engine"),
        )
    return "Backend1"
