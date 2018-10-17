"""
CoordSelect Summary
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import traitlets as tl
import numpy as np

from podpac.core.coordinates import Coordinates
from podpac.core.coordinates import UniformCoordinates1d, ArrayCoordinates1d
from podpac.core.coordinates import make_coord_value, make_coord_delta, add_coord
from podpac.core.node import Node, COMMON_NODE_DOC
from podpac.core.algorithm.algorithm import Algorithm
from podpac.core.utils import common_doc

COMMON_DOC = COMMON_NODE_DOC.copy()

class ExpandCoordinates(Algorithm):
    """Algorithm node used to expand requested coordinates. This is normally used in conjunction with a reduce operation
    to calculate, for example, the average temperature over the last month. While this is simple to do when evaluating
    a single node (just provide the coordinates), this functionality is needed for nodes buried deeper in a pipeline.
    
    Attributes
    ----------
    input_coordinates : podpac.Coordinates
        The coordinates that were used to evaluate the node
    source : podpac.Node
        Source node that will be evaluated with the expanded coordinates.
    lat : List
        Expansion parameters for latitude. Format is ['start_offset', 'end_offset', 'step_size'].
    lon : List
        Expansion parameters for longitude. Format is ['start_offset', 'end_offset', 'step_size'].
    time : List
        Expansion parameters for time. Format is ['start_offset', 'end_offset', 'step_size'].
    alt : List
        Expansion parameters for altitude. Format is ['start_offset', 'end_offset', 'step_size'].
    """
    
    source = tl.Instance(Node)
    input_coordinates = tl.Instance(Coordinates, allow_none=True)
    lat = tl.List().tag(attr=True)
    lon = tl.List().tag(attr=True)
    time = tl.List().tag(attr=True)
    alt = tl.List().tag(attr=True)

    def get_expanded_coordinates1d(self, dim):
        """Returns the expanded coordinates for the requested dimension
        
        Parameters
        ----------
        dim : str
            Dimension to expand
        
        Returns
        -------
        expanded : Coordinates1d
            Expanded coordinates
        
        Raises
        ------
        ValueError
            In case dimension is not in the parameters.
        """
        
        icoords = self.input_coordinates[dim]
        expansion = getattr(self, dim)
        
        if not expansion:  # i.e. if list is empty
            # no expansion in this dimension
            return icoords

        if len(expansion) not in [2, 3]:
            raise ValueError("Invalid expansion attrs for '%s'" % dim)

        # get start and stop offsets
        dstart = make_coord_delta(expansion[0])
        dstop = make_coord_delta(expansion[1])

        if len(expansion) == 2:
            # expand and use native coordinates
            ncoords = self.source.find_coordinates(dim) # TODO
            cs = [ncoords.select((add_coord(x, dstart), add_coord(x, dstop))) for x in icoords.coordinates]

        elif len(expansion) == 3:
            # or expand explicitly
            step = make_coord_delta(expansion[2])
            cs = [UniformCoordinates1d(add_coord(x, dstart), add_coord(x, dstop), step) for x in icoords.coordinates]

        return ArrayCoordinates1d(np.concatenate([c.coordinates for c in cs]), **icoords.properties)

    def get_expanded_coordinates(self):
        """The expanded coordinates
        
        Returns
        -------
        podpac.Coordinates
            The expanded coordinates
        
        Raises
        ------
        ValueError
            Raised if expanded coordinates do not intersect with the source data. For example if a date in the future
            is selected.
        """
        coords = [self.get_expanded_coordinates1d(dim) for dim in self.input_coordinates.dims]
        return Coordinates(coords)
   
    def algorithm(self):
        """Passthrough of the source data
        
        Returns
        -------
        UnitDataArray
            Source evaluated at the expanded coordinates
        """
        return self.source.output
 
    @common_doc(COMMON_DOC)
    def eval(self, coordinates, output=None, method=None):
        """Evaluates this nodes using the supplied coordinates.

        Parameters
        ----------
        coordinates : podpac.Coordinates
            {requested_coordinates}
        output : podpac.UnitsDataArray, optional
            {eval_output}
        method : str, optional
            {eval_method}
            
        Returns
        -------
        {eval_return}
        
        Notes
        -------
        The input coordinates are modified and the passed to the base class implementation of eval.
        """
        self.input_coordinates = coordinates
        coordinates = self.get_expanded_coordinates()
        for dim in coordinates.udims:
            if coordinates[dim].size == 0:
                raise ValueError("Expanded/selected coordinates do not intersect with source data (dim '%s')" % dim)
        return super(ExpandCoordinates, self).eval(coordinates, output, method)


class SelectCoordinates(ExpandCoordinates):
    """Algorithm node used to select coordinates different from the input coordinates. While this is simple to do when 
    evaluating a single node (just provide the coordinates), this functionality is needed for nodes buried deeper in a 
    pipeline. For example, if a single spatial reference point is used for a particular comparison, and this reference
    point is different than the requested coordinates, we need to explicitly select those coordinates using this Node. 
    
    """
    
    def get_expanded_coordinates1d(self, dim):
        """Function name is a misnomer -- should be get_selected_coord, but we are using a lot of the
        functionality of the ExpandCoordinates node. 
        
        Parameters
        ----------
        dim : str
            Dimension for doing the selection
        
        Returns
        -------
        ArrayCoordinates1d
            The selected coordinate
        
        Raises
        ------
        ValueError
            Description
        """
        icoords = self.input_coordinates[dim]
        coords = getattr(self, dim)
        
        if not coords:
            # no selection in this dimension
            return icoords

        if len(coords) not in [1, 2, 3]:
            raise ValueError("Invalid expansion attrs for '%s'" % dim)

        # get start offset
        start = make_coord_value(coords[0])
        
        if len(coords) == 1:
            xcoord = ArrayCoordinates1d(start, **icoords.properties)
            
        elif len(coords) == 2:
            # select and use native coordinates
            stop = make_coord_value(coords[1])
            ncoords = self.source.find_coordinates(dim) #TODO
            xcoord = ncoord.select([start, stop])

        elif len(coords) == 3:
            # select explicitly
            stop = make_coord_value(coords[1])            
            step = make_coord_delta(coords[2])
            xcoord = UniformCoordinates1d(start, stop, step, **icoords.properties)

        return xcoord

