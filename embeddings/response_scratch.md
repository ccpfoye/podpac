# Response to: "How do I make coordinates?"

To make coordinates, you can use the following code in Python:

```
from podpac import Coordinates
Coordinates([lat, lon], dims=['lat', 'lon'])
```

This creates unstacked multidimensional coordinates that form a grid of points. 
You can add a third dimension (e.g. time) like this:

```
from podpac import Coordinates
Coordinates([lat, lon, time], dims=['lat', 'lon', 'time'])
```

You can also create coordinates with just one dimension using the same method as above but with only one coordinate list provided. Additionally, you can define coordinates with an alternate coordinate reference system using the `crs` parameter in the `Coordinates()` function. Finally, grid coordinates can be defined using the `Coordinates()` function with a list of coordinate lists as the argument, and dimension names in a separate `dims` parameter.",

# Response to: "How does caching work?"

PODPAC uses a central cache shared by all nodes. Retrieval from the cache is based on the node's definition (`node.json`), the coordinates, and a key. Each node has a **Cache Control** (`cache_ctrl`) defined by default and the **Cache Control** may contain multiple **Cache Stores** (e.g 'disk', 'ram'). Nodes can cache other data and objects using a cache key and, optionally, coordinates. The node cache can be managed using the `Node.put_cache`, `Node.get_cache`, `Node.has_cache`, and `Node.rem_cache` methods.

# Code-Based

# TypeError: Node.eval() missing 1 required positional argument: 'coordinates'

# For some reason my node isn't caching its output: node = podpac.Node(cache="ram")

# How can I use Coordinates.UniformCoordinates.1d
"Coordinates.UniformCoordinates1d can be used to create uniformly-spaced 1d coordinates. It can be instantiated by specifying `start`, `stop`, and `step` or `size`, where `step` is a signed, nonzero step between coordinates, and `size` is the number of coordinates. Only one of `step` and `size` is allowed. Note that upon initialization, the `step` value may be modified internally to satisfy floating point consistency. The resulting object can then be used as input to create `Coordinates` objects, along with other coordinate objects. \n\nHere is an example code snippet demonstrating the creation of three UniformCoordinates1d objects, which are then used to create a StackedCoordinates object, which is then used to create a Coordinates object:
'```
from podpac.coordinates import UniformCoordinates1d, StackedCoordinates, Coordinates\n\nlat = UniformCoordinates1d(0, 1, size=100, name='lat')
lon = UniformCoordinates1d(10, 20, size=100, name='lon')
time = UniformCoordinates1d(0, 120, size=20, name='time')

stacked_coords = StackedCoordinates([lat, lon, time])
coords = Coordinates([stacked_coords])
```
Note that in the example above, it is assumed that module importation and other required packages have already been handled."
```
# Implement Daymet DataSource Node

To implement a Daymet DataSource node, you can subclass the DataSource node and define the methods to retrieve data (`get_data()`), define the `coordinates` property (`get_native_coordinates()`), and set the necessary properties such as the `source` URL and `interpolation` method.
Here is an example for retrieving Daymet data using the PODPAC DataSource node:
```python
from podpac import DataSource, Coordinates
class DaymetSource(DataSource):
        def get_data(self, coordinates, index):
            # Use requests or other libraries to download data from Daymet at the given coordinates
            data = download_daymet_data(coordinates)
            return data
        def get_native_coordinates(self):
            # Define the native coordinates of the Daymet data using the podpac Coordinates object
            coords = Coordinates([])
            return coords
        
        def __init__(self, variable, year, north, south, east, west, source=None, interpolation=None, nan_vals=None, attrs=None):
            url = f"https://thredds.daac.ornl.gov/thredds/dodsC/daymet-v4/{variable}/{year}/na.ncml"
            boundary = {"bounds": {
                "lat": [south, north],
                "lon": [west, east],
                "time": f"{year}-01-01{year+1}-01-01"
                }
            }
            super().__init__(source=source or url,
                            interpolation=interpolation,
                            nan_vals=nan_vals,
                            attrs=attrs or {},
                            boundary=boundary)
```
You can use this `DaymetSource` class by instantiating it with the necessary arguments, such as the variable (e.g. `tmin`, `tmax`) and the year. Then you can evaluate the node at a given set of coordinates using `node.eval(coordinates)`.

# Transform

To transform WGS84 coordinates to meters, you can use the `transform` function from the `Coordinates` class in PODPAC. You can specify the input CRS as \"EPSG:4326\" (WGS84) and the output CRS as a projection in meters, such as \"EPSG:2193\" for New Zealand Transverse Mercator. Here is an example:

```python
import podpac
# Define WGS84 coordinates
c = podpac.Coordinates([[0, 1], [10, 20, 30, 40], ["2018-01-01", "2018-01-02"]], dims=["lat", "lon", "time"], crs="EPSG:4326")
# Transform to meters using New Zealand Transverse Mercator projection
t = c.transform("EPSG:2193")
```