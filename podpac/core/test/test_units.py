from __future__ import division, unicode_literals, print_function, absolute_import

import pytest
import numpy as np
from pint.errors import DimensionalityError
import traitlets as tl

import podpac.core.node as node

from podpac.core.units import ureg

from podpac.core.node import Node

from podpac.core.units import Units
from podpac.core.units import UnitsNode
from podpac.core.units import UnitsDataArray

class Length(Node):
    units = Units(ureg.meter)

class Area(Node):
    units = Units(ureg.meter ** 2)

class StrictUnitsNode(Node):
    length = UnitsNode().tag(units=ureg.meter)

class TestUnitsNode(object):
    def test_set_length_to_matching_dimension_units_node(self):
        strict_node = StrictUnitsNode()
        l = Length()
        strict_node.length = l

    def test_set_length_to_different_dimension_units_node_throws_error(self):
        strict_node = StrictUnitsNode()
        a = Area()
        with pytest.raises(DimensionalityError):
            strict_node.length = a

    def test_set_length_to_number_throws_error(self):
        strict_node = StrictUnitsNode()
        with pytest.raises(tl.TraitError):
            strict_node.length = 10


class TestUnits(object):
    def test_set_units_to_related_unit(self):
        l = Length()
        l.units = ureg.feet

    def test_set_units_to_unrelated_unit(self):
        a = Area()
        a.units = ureg.meter

    def test_set_units_to_string_throws_error(self):
        l = Length()
        with pytest.raises(tl.TraitError):
            l.units = 'meter'

class TestUnitDataArray(object):
    def test_no_units_to_base_units_has_no_units(self):
        a = UnitsDataArray(
                np.arange(24, dtype=np.float64).reshape((3, 4, 2)),
                coords={'x': np.arange(3), 'y': np.arange(4)*10, 'z': np.arange(2)+100},
                dims=['x', 'y', 'z'])
        b = a.to_base_units()
        assert b.attrs.get("units", None) is None
 

    def test_mean_passes_units_while_sum_does_not(self):
        n_lats = 3
        n_lons = 4
        n_alts = 2
        a = UnitsDataArray(np.arange(n_lats*n_lons*n_alts).reshape((n_lats,n_lons,n_alts)), 
                            dims=['lat', 'lon', 'alt'],
                            attrs={'units': ureg.meter})
        assert a.mean(axis=0).attrs.get("units", None) is not None
        assert a.sum(axis=0).attrs.get("units", None) is None

    def test_set_to_value_using_UnitsDataArray_as_mask_broadcasts_to_dimensions_not_in_mask(self):
        a = UnitsDataArray(
                np.arange(24, dtype=np.float64).reshape((3, 4, 2)),
                coords={'x': np.arange(3), 'y': np.arange(4)*10, 'z': np.arange(2)+100},
                dims=['x', 'y', 'z'])
        b = a[0, :, :]
        b = b<3

        mask = b.transpose(*('z','y'))
        value = np.nan

        a.set(value, mask)
        # dims of a remain unchanged
        assert np.all(np.array(a.dims) == np.array(('x', 'y', 'z')))
        # shape of a remains unchanged
        assert np.all(np.array(a.values.shape) == np.array((3, 4, 2)))
        # a.set was broadcast across the 'x' dimension 
        for x in range(3):
            for y in range(4):
                for z in range(2):
                    if y == 0 and (z==0 or z==1):
                        assert np.isnan(a[x,y,z])
                    elif y == 1 and z == 0:
                        assert np.isnan(a[x,y,z])
                    else:
                        assert not np.isnan(a[x,y,z])

    def test_get_item_with_1d_units_data_array_as_key_boradcasts_to_correct_dimension(self):
        a = UnitsDataArray(
                np.arange(24).reshape((3, 4, 2)),
                coords={'x': np.arange(3), 'y': np.arange(4)*10, 'z': np.arange(2)+100},
                dims=['x', 'y', 'z'])
        b = a[0, :, 0]
        b = b<3
        c = a[b]
        # dims of a remain unchanged
        assert np.all(np.array(a.dims) == np.array(('x', 'y', 'z')))
        # shape of a remains unchanged
        assert np.all(np.array(a.values.shape) == np.array((3, 4, 2)))
        # dims of a remain unchanged
        assert np.all(np.array(c.dims) == np.array(('x', 'y', 'z')))
        # shape of a remains unchanged
        assert np.all(np.array(c.values.shape) == np.array((3, 2, 2)))
        # a[b] was broadcast across the 'y' dimension 
        for x in range(3):
            for y in range(2):
                for z in range(2):
                    c[x,y,z] in [ 0,  1,  2,  3,  8,  9, 10, 11, 16, 17, 18, 19]


    def test_get_item_with_units_data_array_as_key_throws_index_error(self):
        """
        I believe this is not the desired behavior. We should look at this function.
        """
        a = UnitsDataArray(
                np.arange(24, dtype=np.float64).reshape((3, 4, 2)),
                coords={'x': np.arange(3), 'y': np.arange(4)*10, 'z': np.arange(2)+100},
                dims=['x', 'y', 'z'])
        b = a < 3
        with pytest.raises(IndexError):
            a[b]


    def test_partial_transpose_specify_just_lon_swaps_lat_lon(self):
        n_lats = 3
        n_lons = 4
        lat_lon = UnitsDataArray(np.arange(12).reshape((n_lats,n_lons)), 
                            dims=['lat', 'lon'],
                            attrs={'units': ureg.meter})
        lon_lat = lat_lon.part_transpose(['lon'])
        for lat in range(n_lats):
            for lon in range(n_lons):
                lat_lon[lat,lon] == lon_lat[lon,lat]

    def test_partial_transpose_specify_both_swaps_lat_lon(self):
        n_lats = 3
        n_lons = 4
        lat_lon = UnitsDataArray(np.arange(12).reshape((n_lats,n_lons)), 
                            dims=['lat', 'lon'],
                            attrs={'units': ureg.meter})
        lon_lat = lat_lon.part_transpose(['lon', 'lat'])
        for lat in range(n_lats):
            for lon in range(n_lons):
                lat_lon[lat,lon] == lon_lat[lon,lat]
    
    def test_partial_transpose_specify_none_leaves_lat_lon_untouched(self):
        n_lats = 3
        n_lons = 4
        lat_lon = UnitsDataArray(np.arange(12).reshape((n_lats,n_lons)), 
                            dims=['lat', 'lon'],
                            attrs={'units': ureg.meter})
        lat_lon_2 = lat_lon.part_transpose([])
        for lat in range(n_lats):
            for lon in range(n_lons):
                lat_lon[lat,lon] == lat_lon_2[lat,lon]

    def test_no_units_coord(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={})    
        a3 = a1 + a2
        a3b = a2 + a1
        a4 = a1 > a2
        a5 = a1 < a2
        a6 = a1 == a2
        a7 = a1 * a2
        a8 = a2 / a1
        a9 = a1 // a2
        a10 = a1 % a2        
        
    def test_first_units_coord(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={'units': ureg.meter})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={})    
        with pytest.raises(DimensionalityError):
            a3 = a1 + a2
        with pytest.raises(DimensionalityError):
            a3b = a2 + a1
        with pytest.raises(DimensionalityError):
            a4 = a1 > a2
        with pytest.raises(DimensionalityError):
            a5 = a1 < a2
        with pytest.raises(DimensionalityError):
            a6 = a1 == a2
        a7 = a1 * a2
        a8 = a2 / a1
        with pytest.raises(DimensionalityError):
            a9 = a1 // a2
        with pytest.raises(DimensionalityError):
            a10 = a1 % a2        

    def test_second_units_coord(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={'units': ureg.inch})    
        with pytest.raises(DimensionalityError):
            a3 = a1 + a2
        with pytest.raises(DimensionalityError):
            a3b = a2 + a1
        with pytest.raises(DimensionalityError):
            a4 = a1 > a2
        with pytest.raises(DimensionalityError):
            a5 = a1 < a2
        with pytest.raises(DimensionalityError):
            a6 = a1 == a2
        a7 = a1 * a2
        a8 = a2 / a1
        with pytest.raises(DimensionalityError):
            a9 = a1 // a2
        with pytest.raises(DimensionalityError):
            a10 = a1 % a2        
        
    def test_units_allpass(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={'units': ureg.meter})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                           attrs={'units': ureg.inch})    
        a3 = a1 + a2
        assert a3[0, 0].data[()] == (1*ureg.meter + 1*ureg.inch).to(ureg.meter).magnitude

        a3b = a2 + a1
        assert a3b[0, 0].data[()] == (1*ureg.meter + 1*ureg.inch).to(ureg.inch).magnitude
        
        a4 = a1 > a2
        assert a4[0, 0].data[()] == True

        a5 = a1 < a2
        assert a5[0, 0].data[()] == False
        
        a6 = a1 == a2
        assert a6[0, 0].data[()] == False

        a7 = a1 * a2
        assert a7[0, 0].to(ureg.m**2).data[()] == (1*ureg.meter*ureg.inch).to(ureg.meter**2).magnitude

        a8 = a2 / a1
        assert a8[0, 0].to_base_units().data[()] == (1*ureg.inch/ureg.meter).to_base_units().magnitude

        a9 = a1 // a2
        assert a9[0, 0].to_base_units().data[()] == ((1*ureg.meter) // (1*ureg.inch)).to_base_units().magnitude
        
        a10 = a1 % a2
        assert a10[0, 0].to_base_units().data[()] == ((1*ureg.meter) % (1*ureg.inch)).to_base_units().magnitude
    
    def test_units_somefail(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                               attrs={'units': ureg.meter})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                               attrs={'units': ureg.kelvin})    
        with pytest.raises(DimensionalityError):
            a3 = a1 + a2
        with pytest.raises(DimensionalityError):
            a3b = a2 + a1
        with pytest.raises(DimensionalityError):
            a4 = a1 > a2
        with pytest.raises(DimensionalityError):
            a5 = a1 < a2
        with pytest.raises(DimensionalityError):
            a6 = a1 == a2
        
        a7 = a1 * a2
        assert a7[0, 0].to(ureg.meter * ureg.kelvin).data[()] == (1*ureg.meter*ureg.kelvin).magnitude

        a8 = a1 / a2
        assert a8[0, 0].to(ureg.meter / ureg.kelvin).data[()] == (1*ureg.meter/ureg.kelvin).magnitude
        
        with pytest.raises(DimensionalityError):
            a9 = a1 // a2
        
        with pytest.raises(DimensionalityError):
            a10 = a1 % a2        
            
    def test_ufuncs(self):
        a1 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                               attrs={'units': ureg.meter})
        a2 = UnitsDataArray(np.ones((4,3)), dims=['lat', 'lon'],
                               attrs={'units': ureg.kelvin}) 
        
        np.sqrt(a1)
        np.mean(a1)
        np.min(a1)
        np.max(a1)
        a1 ** 2
        
        # These don't have units!
        np.dot(a2.T, a1)
        np.std(a1)
        np.var(a1)        

