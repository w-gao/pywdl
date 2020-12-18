#
# Modified from https://github.com/DataBiosphere/toil/blob/master/src/toil/wdl/wdl_types.py
# under the Apache v2 License:
#

# Copyright (C) 2015-2021 Regents of the University of California
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC


class WDLType:
    """
    Represents a primitive or compound WDL type:

    https://github.com/openwdl/wdl/blob/main/versions/development/SPEC.md#types
    """
    def __init__(self, optional: bool = False):
        self.optional = optional

    @property
    def name(self) -> str:
        """
        Type name as string. Used in display messages / 'mappings.out' if dev
        mode is enabled.
        """
        raise NotImplementedError

    def __eq__(self, other):
        return self.name.__eq__(other)

    def __str__(self):
        return self.name.__str__()

    def __repr__(self):
        return self.name.__repr__()


class WDLCompoundType(WDLType, ABC):
    """
    Represents a WDL compound type.
    """
    pass


class WDLStringType(WDLType):
    """ Represents a WDL String primitive type."""

    @property
    def name(self) -> str:
        return 'String'


class WDLIntType(WDLType):
    """ Represents a WDL Int primitive type."""

    @property
    def name(self) -> str:
        return 'Int'


class WDLFloatType(WDLType):
    """ Represents a WDL Float primitive type."""

    @property
    def name(self) -> str:
        return 'Float'


class WDLBooleanType(WDLType):
    """ Represents a WDL Boolean primitive type."""
    @property
    def name(self) -> str:
        return 'Boolean'


class WDLFileType(WDLType):
    """ Represents a WDL File primitive type."""
    @property
    def name(self) -> str:
        return 'File'


class WDLArrayType(WDLCompoundType):
    """ Represents a WDL Array compound type."""
    def __init__(self, element: WDLType, optional: bool = False):
        super().__init__(optional)
        self.element = element

    @property
    def name(self) -> str:
        return f'Array[{self.element.name}]'


class WDLPairType(WDLCompoundType):
    """ Represents a WDL Pair compound type."""
    def __init__(self, left: WDLType, right: WDLType, optional: bool = False):
        super().__init__(optional)
        self.left = left
        self.right = right

    @property
    def name(self) -> str:
        return f'Pair[{self.left.name}, {self.right.name}]'


class WDLMapType(WDLCompoundType):
    """ Represents a WDL Map compound type."""
    def __init__(self, key: WDLType, value: WDLType, optional: bool = False):
        super().__init__(optional)
        self.key = key
        self.value = value

    @property
    def name(self) -> str:
        return f'Map[{self.key.name}, {self.value.name}]'
