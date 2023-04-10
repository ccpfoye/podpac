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

