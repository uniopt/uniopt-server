"""
This file is only used for demo using a default idf file
"""

from EPinterface.EPHelper import EnergyPlusHelper
import os

current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

ep = EnergyPlusHelper(idf_path="%s/singleZonePurchAir_template.idf" % current_dir,
                      output_path="%s/out" % current_dir)

# prints a VERY big dict containing everything inside the idf file indexed by object
print(ep.get_all_objects())
"""
prints the list of values of [BUILDING: North Axis] as there could be more than one
BUILDING object so it returns a list also it can retrieve more than field at the same
time e.g.
    >>> ep.get_field_val(["BUILDING","HeatBalanceAlgorithm"], ["North_Axis","Algorithm"])
it'll return a list respectively.

NOTE: the fields with space in the name must be replaced with an underscore _
"""
print(ep.get_field_val(["BUILDING"], ["North_Axis"]))
"""
will set a value (or) values just like the get function using the order of the given list

NOTE: the function replaces every occurrence of the give field in the given object, it will edit
the value for each object not just one.
"""
ep.set_field_val(["BUILDING"], ["North_Axis"], ["32.0"])
# to check if the value was edited
print(ep.get_field_val(["BUILDING"], ["North_Axis"]))
# runs the idf internal structure (edited not the original file)
ep.run_idf()
# get_results() processes the eso (output form of the output variables) and returns a dict
# structured as [variable data (name, code, running mode{Daily, seasonally etc..} and unit ] , [values]
e = ep.get_results()

print(e)

