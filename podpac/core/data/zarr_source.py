import traitlets as tl
import numpy as np

from lazy_import import lazy_module, lazy_class

zarr = lazy_module("zarr")
zarrGroup = lazy_class("zarr.Group")

from podpac.core.utils import common_doc
from podpac.core.data.datasource import COMMON_DATA_DOC, DATA_DOC
from podpac.core.data.file_source import BaseFileSource, FileKeysMixin


class Zarr(FileKeysMixin, BaseFileSource):
    """Create a DataSource node using zarr.
    
    Attributes
    ----------
    source : str
        Path to the Zarr archive
    file_mode : str, optional
        Default is 'r'. The mode used to open the Zarr archive. Options are r, r+, w, w- or x, a.
    dataset : zarr.Group
        The h5py file object used to read the file
    native_coordinates : Coordinates
        {native_coordinates}
    data_key : str, int
        data key, default 'data'
    lat_key : str, int
        latitude coordinates key, default 'lat'
    lon_key : str, int
        longitude coordinates key, default 'lon'
    time_key : str, int
        time coordinates key, default 'time'
    alt_key : str, int
        altitude coordinates key, default 'alt'
    crs : str
        Coordinate reference system of the coordinates
    cf_time : bool
        decode CF datetimes
    cf_units : str
        units, when decoding CF datetimes
    cf_calendar : str
        calendar, when decoding CF datetimes
    """

    file_mode = tl.Unicode(default_value="r").tag(readonly=True)
    coordinate_index_type = "slice"

    # s3 credentials
    # TODO factor out
    access_key_id = tl.Unicode()
    secret_access_key = tl.Unicode()
    region_name = tl.Unicode()

    @tl.default("access_key_id")
    def _get_access_key_id(self):
        return settings["AWS_ACCESS_KEY_ID"]

    @tl.default("secret_access_key")
    def _get_secret_access_key(self):
        return settings["AWS_SECRET_ACCESS_KEY"]

    @tl.default("region_name")
    def _get_region_name(self):
        return settings["AWS_REGION_NAME"]

    @property
    def dataset(self):
        if not hasattr(self, "_dataset"):
            if self.source.startswith("s3://"):
                root = self.source.strip("s3://")
                kwargs = {"region_name": self.region_name}
                s3 = s3fs.S3FileSystem(key=self.access_key_id, secret=self.secret_access_key, client_kwargs=kwargs)
                s3map = s3fs.S3Map(root=root, s3=s3, check=False)
                store = s3map
            else:
                store = str(self.source)  # has to be a string in Python2.7 for local files

            try:
                return zarr.open(store, mode=self.file_mode)
            except ValueError:
                raise ValueError("No Zarr store found at path '%s'" % self.source)

        return self._dataset

    # -------------------------------------------------------------------------
    # public api methods
    # -------------------------------------------------------------------------

    @property
    def dims(self):
        if not hasattr(self, "_dims"):
            key = self.data_key or self.output_keys[0]

            try:
                self._dims = self.dataset[key].attrs["_ARRAY_DIMENSIONS"]
            except:
                lookup = {self.lat_key: "lat", self.lon_key: "lon", self.alt_key: "alt", self.time_key: "time"}
                self._dims = [lookup[key] for key in self.dataset if key in lookup]

        return self._dims

    @property
    def keys(self):
        return list(self.dataset.keys())

    @common_doc(COMMON_DATA_DOC)
    def get_data(self, coordinates, coordinates_index):
        """{get_data}
        """
        data = self.create_output_array(coordinates)
        if self.data_key is not None:
            data[:] = self.dataset[self.data_key][coordinates_index]
        else:
            for key, name in zip(self.output_keys, self.outputs):
                data.sel(output=name)[:] = self.dataset[key][coordinates_index]
        return data
