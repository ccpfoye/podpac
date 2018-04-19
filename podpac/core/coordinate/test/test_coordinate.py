
import sys
from collections import OrderedDict

import pytest
import traitlets as tl
import numpy as np
from six import string_types

from podpac.core.coordinate import Coordinate, CoordinateGroup

class TestBaseCoordinate(object):
    def test_abstract_methods(self):
        from podpac.core.coordinate import BaseCoordinate
        c = BaseCoordinate()

        with pytest.raises(NotImplementedError):
            c.stack([])

        with pytest.raises(NotImplementedError):
            c.unstack()

        with pytest.raises(NotImplementedError):
            c.intersect(c)

class TestCoordinate(object):
    @pytest.mark.skipif(sys.version >= '3.6', reason="Python <3.6 compatibility")
    def test_order(self):
        # required
        with pytest.raises(TypeError):
            Coordinate(lat=0.25, lon=0.3)

        # not required
        Coordinate(lat=0.25)
        
        # not required
        Coordinate(coords=OrderedDict(lat=0.25, lon=0.3))

        # invalid
        with pytest.raises(ValueError):
            Coordinate(lon=0.3, lat=0.25, order=['lat', 'lon', 'time'])

        # invalid
        with pytest.raises(ValueError):
            Coordinate(lon=0.3, lat=0.25, order=['lat'])

        # valid
        c = Coordinate(lon=0.3, lat=0.25, order=['lat', 'lon'])
        assert c.dims == ['lat', 'lon']
        
        c = Coordinate(lon=0.3, lat=0.25, order=['lon', 'lat'])
        assert c.dims == ['lon', 'lat']

    @pytest.mark.skipif(sys.version < '3.6', reason="Python >=3.6 required")
    def test_order_detect(self):
        coord = Coordinate(lat=0.25, lon=0.3)
        assert coord.dims == ['lat', 'lon']

        coord = Coordinate(lon=0.3, lat=0.25)
        assert coord.dims == ['lon', 'lat']

        # in fact, ignore order
        coord = Coordinate(lon=0.3, lat=0.25, order=['lat', 'lon'])
        assert coord.dims == ['lon', 'lat']

    def _common_checks(self, coord, expected_dims, expected_shape, stacked):
        # note: check stacked dims_map manually

        assert coord.dims == expected_dims
        assert coord.shape == expected_shape
        assert coord.is_stacked == stacked
        
        # dims map and coords
        assert isinstance(coord.dims_map, dict)
        assert isinstance(coord.coords, OrderedDict)
        for dim in expected_dims:
            if not coord.is_stacked:
                assert coord.dims_map[dim] == dim
            assert isinstance(coord.coords[dim], np.ndarray)

        # additional properties
        assert isinstance(coord.kwargs, dict)
        assert isinstance(coord.latlon_bounds_str, string_types)

    def test_coords_empty(self):
        coord = Coordinate()
        
        self._common_checks(coord, [], (), False)
        assert len(coord.dims_map.keys()) == 0
        assert len(coord.coords.keys()) == 0

        assert coord.ctype == 'segment' # TODO move
        assert coord.segment_position == 0.5 # TODO move
        assert coord.coord_ref_sys == 'WGS84' # TODO move
        assert coord.gdal_crs == 'EPSG:4326' # TODO move

    def test_coords_single_latlon(self):
        coord = Coordinate(lat=0.25, lon=0.3, order=['lat', 'lon'])
        
        self._common_checks(coord, ['lat', 'lon'], (1, 1), False)
        np.testing.assert_array_equal(coord.coords['lat'], [0.25])
        np.testing.assert_array_equal(coord.coords['lon'], [0.3])

    def test_coords_single_datetime(self):
        coord = Coordinate(time='2018-01-01')

        self._common_checks(coord, ['time'], (1,), False)
        np.testing.assert_array_equal(coord.coords['time'], np.datetime64('2018-01-01'))

    def test_coords_single_time_dependent(self):
        coord = Coordinate(lat=0.25, lon=0.3, time='2018-01-01', order=['lat', 'lon', 'time'])
        
        self._common_checks(coord, ['lat', 'lon', 'time'], (1, 1, 1), False)
        np.testing.assert_array_equal(coord.coords['lat'], [0.25])
        np.testing.assert_array_equal(coord.coords['lon'], [0.3])
        np.testing.assert_array_equal(coord.coords['time'], np.datetime64('2018-01-01'))

    def test_coords_single_latlon_stacked(self):
        coord = Coordinate(lat_lon=[0.25, 0.3])
        
        self._common_checks(coord, ['lat_lon'], (1,), True)
        assert coord.dims_map['lat'] == 'lat_lon'
        assert coord.dims_map['lon'] == 'lat_lon'
        np.testing.assert_array_equal(coord.coords['lat_lon']['lat'], [0.25])
        np.testing.assert_array_equal(coord.coords['lat_lon']['lon'], [0.3])

    def test_coords_single_time_dependent_stacked(self):
        coord = Coordinate(lat_lon=[0.25, 0.3], time='2018-01-01', order=['lat_lon', 'time'])
        
        self._common_checks(coord, ['lat_lon', 'time'], (1, 1), True)
        assert coord.dims_map['lat'] == 'lat_lon'
        assert coord.dims_map['lon'] == 'lat_lon'
        assert coord.dims_map['time'] == 'time'
        np.testing.assert_array_equal(coord.coords['lat_lon']['lat'], [0.25])
        np.testing.assert_array_equal(coord.coords['lat_lon']['lon'], [0.3])
        np.testing.assert_array_equal(coord.coords['time'], np.datetime64('2018-01-01'))

    def test_coords_latlon_coord(self):
        coord = Coordinate(lat=[0.2, 0.4, 0.5], lon=[0.3, -0.1], order=['lat', 'lon'])
        
        self._common_checks(coord, ['lat', 'lon'], (3, 2), False)
        np.testing.assert_array_equal(coord.coords['lat'], [0.2, 0.4, 0.5])
        np.testing.assert_array_equal(coord.coords['lon'], [0.3, -0.1])

    def test_coords_latlon_coord_stacked(self):
        coord = Coordinate(lat_lon=[[0.2, 0.4, 0.5], [0.3, -0.1, 0.2]])
        
        self._common_checks(coord, ['lat_lon'], (3,), True)
        np.testing.assert_array_equal(coord.coords['lat_lon']['lat'], [0.2, 0.4, 0.5])
        np.testing.assert_array_equal(coord.coords['lat_lon']['lon'], [0.3, -0.1, 0.2])

    def test_coords_datetime_coord(self):
        coord = Coordinate(time=['2018-01-01', '2018-01-02', '2018-02-01'])

        self._common_checks(coord, ['time'], (3,), False)
        np.testing.assert_array_equal(
            coord.coords['time'],
            np.array(['2018-01-01', '2018-01-02', '2018-02-01']).astype(np.datetime64))

    def test_coords_time_dependent_coord_stacked(self):
        coord = Coordinate(
            lat_lon=[[0.2, 0.4, 0.5], [0.3, -0.1, 0.2]],
            time=['2018-01-01', '2018-01-02', '2018-02-01'],
            order=['lat_lon', 'time'])
        
        self._common_checks(coord, ['lat_lon', 'time'], (3, 3), True)
        np.testing.assert_array_equal(coord.coords['lat_lon']['lat'], [0.2, 0.4, 0.5])
        np.testing.assert_array_equal(coord.coords['lat_lon']['lon'], [0.3, -0.1, 0.2])
        np.testing.assert_array_equal(
            coord.coords['time'],
            np.array(['2018-01-01', '2018-01-02', '2018-02-01']).astype(np.datetime64))

    def test_coords_latlon_uniform(self):
        pass

    def test_coords_latlon_uniform_stacked(self):
        pass

    def test_coords_datetime_uniform(self):
        pass

    def test_coords_time_dependent_uniform_stacked(self):
        pass

    def test_coords_time_dependent_mixed(self):
        pass

    def test_coords_time_dependent_mixed_stacked(self):
        pass

    def test_coords_explicit_coords(self):
        c1 = Coordinate(lat=0.25, lon=0.3, order=['lat', 'lon'])
        
        coords = OrderedDict()
        coords['lat'] = 0.25
        coords['lon'] = 0.3
        c2 = Coordinate(coords=coords)
        
        assert c1.dims == c2.dims
        assert c1.coords['lat'] == c2.coords['lat']
        assert c1.coords['lon'] == c2.coords['lon']
        
        with pytest.raises(TypeError):
            Coordinate(coords=[0.25])

        with pytest.raises(TypeError):
            Coordinate(coords={'lat': 0.25, 'lon': 0.3})

    def test_coords_explicit_coord(self):
        from podpac.core.coordinate import Coord
        coord = Coordinate(lat=Coord([0.2, 0.4, 0.5]), lon=[0.3, -0.1], order=['lat', 'lon'])
        
        self._common_checks(coord, ['lat', 'lon'], (3, 2), False)
        np.testing.assert_array_equal(coord.coords['lat'], [0.2, 0.4, 0.5])
        np.testing.assert_array_equal(coord.coords['lon'], [0.3, -0.1])

    def test_coords_invalid(self):
        pass

    @pytest.mark.skip(reason="coordinate refactor")
    def test_unstacked_regular(self):
        coord = Coordinate(lat=(0, 1, 4), lon=(0, 1, 4), 
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=[0, 1, 4], lon=[0, 1, 4], 
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=(0, 1, 1/4), lon=(0, 1, 1/4), 
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=[0, 1, 1/4], lon=[0, 1, 1/4], 
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        
    @pytest.mark.skip(reason="coordinate refactor")
    def test_unstacked_irregular(self):
        coord = Coordinate(lat=np.linspace(0, 1, 4), lon=np.linspace(0, 1, 4),
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        
    @pytest.mark.skip(reason="coordinate refactor")
    def test_unstacked_dependent(self):
        coord = Coordinate(
            lat=xr.DataArray(
                np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[0], 
                dims=['lat', 'lon']),
            lon=xr.DataArray(
                np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[0], 
                dims=['lat', 'lon']),
            order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        
    @pytest.mark.skip(reason="coordinate refactor")
    def test_stacked_regular(self):
        coord = Coordinate(lat=((0, 0), (1, -1), 4), lon=((0, 0), (1, -1), 4),
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=[(0, 0), (1, -1), 4], lon=[(0, 0), (1, -1), 4],
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=((0, 0), (1, -1), 1/4), lon=((0, 0), (1, -1), 1/4),
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(lat=[(0, 0), (1, -1), 1/4], lon=[(0, 0), (1, -1), 1/4],
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        
    @pytest.mark.skip(reason="coordinate refactor")
    def test_stacked_irregular(self):
        coord = Coordinate(lat=np.column_stack((np.linspace(0, 1, 4),
                                              np.linspace(0, -1, 4))),
                           lon=np.column_stack((np.linspace(0, 1, 4),
                                              np.linspace(0, -1, 4))),
                           order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        
    @pytest.mark.skip(reason="coordinate refactor")
    def test_stacked_dependent(self):
        coord = Coordinate(
            lat=[
                xr.DataArray(
                         np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[0],
                         dims=['lat-lon', 'time']), 
                xr.DataArray(
                    np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[1],
                             dims=['lat-lon', 'time'])        
                ], 
            lon=[
                xr.DataArray(
                    np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[0],
                    dims=['lat-lon', 'time']), 
                xr.DataArray(
                    np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5))[1],
                    dims=['lat-lon', 'time']),
                
                ], 
            order=['lat', 'lon'])
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))        
        coord = Coordinate(
            lat=xr.DataArray(np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5)),
                             dims=['stack', 'lat-lon', 'time']), 
            lon=xr.DataArray(np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, -1, 5)),
                         dims=['stack', 'lat-lon', 'time']), 
            order=['lat', 'lon']
        )
        np.testing.assert_array_equal(np.array(coord.intersect(coord)._coords['lat'].bounds),
                                          np.array(coord._coords['lat'].bounds))

class TestCoordIntersection(object):
    @pytest.mark.skip(reason="coordinate refactor")
    def test_regular(self):
        coord = Coord(coords=(1, 10, 10))
        coord_left = Coord(coords=(-2, 7, 10))
        coord_right = Coord(coords=(4, 13, 10))
        coord_cent = Coord(coords=(4, 7, 4))
        coord_cover = Coord(coords=(-2, 13, 15))
        
        c = coord.intersect(coord).coordinates
        np.testing.assert_array_equal(c, coord.coordinates)
        c = coord.intersect(coord_cover).coordinates
        np.testing.assert_array_equal(c, coord.coordinates)        
        
        c = coord.intersect(coord_left).coordinates
        np.testing.assert_array_equal(c, coord.coordinates[:8])                
        c = coord.intersect(coord_right).coordinates
        np.testing.assert_array_equal(c, coord.coordinates[2:])
        c = coord.intersect(coord_cent).coordinates
        np.testing.assert_array_equal(c, coord.coordinates[2:8])

class TestCoordinateGroup(object):
    def test_init(self):
        c1 = Coordinate(
            lat=(0, 10, 5),
            lon=(0, 20, 5),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        c2 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        c3 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            time='2018-01-01',
            order=('time', 'lat', 'lon'))

        c4 = Coordinate(
            lat_lon=((0, 10, 5), (0, 20, 5)),
            time='2018-01-01',
            order=('lat_lon', 'time'))

        c5 = Coordinate(
            lat=(0, 20, 15),
            lon=(0, 20, 15),
            order=('lat', 'lon'))

        c6 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            order=('lat', 'lon'))

        # empty init
        g = CoordinateGroup()
        g = CoordinateGroup([])
        
        # basic init (with mismatched stacking, ordering, shapes)
        g = CoordinateGroup([c1])
        g = CoordinateGroup([c1, c2, c3, c4])
        g = CoordinateGroup([c5, c6])
        
        # list is required
        with pytest.raises(tl.TraitError):
            CoordinateGroup(c1)
        
        # Coord objects not valid
        with pytest.raises(tl.TraitError):
            CoordinateGroup([c1['lat']])

        # CoordinateGroup objects not valid (no nesting)
        g = CoordinateGroup([c1, c2])
        with pytest.raises(tl.TraitError):
            CoordinateGroup([g])

        # dimensions must match
        with pytest.raises(ValueError):
            CoordinateGroup([c1, c5])

    def test_len(self):
        c1 = Coordinate(
            lat=(0, 10, 5),
            lon=(0, 20, 5),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        c2 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        g = CoordinateGroup()
        assert len(g) == 0
        
        g = CoordinateGroup([])
        assert len(g) == 0
        
        g = CoordinateGroup([c1])
        assert len(g) == 1
        
        g = CoordinateGroup([c1, c2])
        assert len(g) == 2

    def test_dims(self):
        c1 = Coordinate(
            lat=(0, 10, 5),
            lon=(0, 20, 5),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        c2 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            time='2018-01-01',
            order=('lat', 'lon', 'time'))

        c3 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            time='2018-01-01',
            order=('time', 'lat', 'lon'))

        c4 = Coordinate(
            lat_lon=((0, 10, 5), (0, 20, 5)),
            time='2018-01-01',
            order=('lat_lon', 'time'))

        c5 = Coordinate(
            lat=(0, 20, 15),
            lon=(0, 20, 15),
            order=('lat', 'lon'))

        c6 = Coordinate(
            lat=(10, 20, 15),
            lon=(10, 20, 15),
            order=('lat', 'lon'))

        g = CoordinateGroup()
        assert len(g.dims) == 0

        g = CoordinateGroup([c1])
        assert g.dims == {'lat', 'lon', 'time'}

        g = CoordinateGroup([c1, c2, c3, c4])
        assert g.dims == {'lat', 'lon', 'time'}

        g = CoordinateGroup([c4])
        assert g.dims == {'lat', 'lon', 'time'}

        g = CoordinateGroup([c5, c6])
        assert g.dims == {'lat', 'lon'}

    @pytest.mark.skip(reason="unwritten test")
    def test_iter(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_getitem(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_intersect(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_add(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_iadd(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_append(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_stack(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_unstack(self):
        pass

    @pytest.mark.skip(reason="unwritten test")
    def test_iterchunks(self):
        pass

