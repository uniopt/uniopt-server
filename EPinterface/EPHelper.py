import os
from eppy.modeleditor import IDF
from eppy.idf_helpers import getidfobjectlist
from collections import OrderedDict
from EPinterface.esoReader import esoreader as eso


class EnergyPlusHelper:
    """ A class for the EnergyPlus communicator
    """

    def __init__(self,
                 idf_path,
                 idd_path=None,
                 weather_path=None,
                 output_path=None,
                 ):
        """ New instance of the `EnergyPlusHelper` class

        Parameters
        ----------
        idf_path : string
            the file name with extension (.idf) of the input file to simulate. With a relative path if not in the same
            running directory.
        idd_path : string
            the Input data dictionary path (.idd)
        weather_path : string
            the weather file path. (.epw)
        output_path : string
            the directory to output the result files in. Default is the same directory
        Examples
        ----------
        >>> from EPinterface.EPHelper import EnergyPlusHelper
        >>> ep = EnergyPlusHelper(idf_path="path to idf",
        >>>                         idd_path="path to idd",weather_path="path to weather")
        """
        self.idf_path = idf_path
        self.idd_path = idd_path
        # TODO: handle the weather file path
        # self.weather_path = "/mnt/c/EnergyPlusV9-1-0/WeatherData/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
        self.weather_path = "C:/EnergyPlusV9-1-0/WeatherData/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
        self.output_path = output_path
        self.run_filename = "in.idf"
        # IDF.setiddname(idd_path) if self.idf_file else 1
        # TODO : get the path of E+ install as the default .idd is needed.
        # IDF.setiddname("/mnt/d/F/uniopt/EP/Energy+.idd")
        IDF.setiddname("D:/F/uniopt/EP/Energy+.idd")
        self.idf = IDF(self.idf_path, self.weather_path)

    def get_all_objects(self):
        """ returns all the idf file objects

        Returns
        -------
        Iterable
            list of idf objects as dictionaries

        """
        objects = []
        for obj in getidfobjectlist(self.idf):
            one_obj = list(zip(obj.fieldnames, obj.fieldvalues))
            # TODO: prior to Python 3.6 Dicts are not ordered and cannot be forced to be
            #  alt solution :   one_obj = OrderedDict(one_obj)
            #  but we'll need to find a way to dump it into JSON for the ui to be ordered
            dict_obj = {}
            for (k, v) in one_obj:
                dict_obj[k] = v
            objects.append(dict_obj)
        return objects

    def get_object_fields(self, obj_name):
        """ returns the list of all object fields

        Parameters
        ----------
        obj_name : string
            name of the object to get the fields for

        Returns
        -------
        Iterable
            list of the fields of the object.
            TODO : Handle the return of multiple objects, they will have the same name in the UI.
            https://eppy.readthedocs.io/en/latest/Main_Tutorial.html#working-with-e-objects
        """
        objects = self.idf.idfobjects[obj_name]
        fields = []
        for obj in objects:
            for field in obj.fieldnames:
                fields.append({field: getattr(obj, field)})
        return fields

    def get_field_val(self, obj_name, fld_name):
        """ get multiple fields of multiple objects at once

        Parameters
        ----------
        obj_name : list
            list of the objects names
        fld_name : list
            list of fields names

        Returns
        -------
        Iterable
            list of values


        """
        fields = []
        for obj_name, fld_name in zip(obj_name, fld_name):
            # TODO: multiple objects same name?
            obj = self.idf.idfobjects[obj_name]
            for Oneobj in obj:
                fields.append(getattr(Oneobj, fld_name))

        return fields

    def set_field_val(self, obj_name, fld_name, val):
        """ set multiple fields of multiple objects at once

        Parameters
        ----------
        obj_name : list
            list of the objects names
        fld_name : list
            list of fields names
        val : list
            list of values.

        Examples
        ----------
        >>> ep = EnergyPlusHelper(idf_path="D:/F/uniopt/EP/singleZonePurchAir_template.idf",
        >>>                         idd_path="D:/F/uniopt/EP/E+.idd",weather_path="D:/F/uniopt/EP/in.epw")
        >>> ep.set_field_val(obj_name=['BUILDING','MATERIAL'], fld_name=['North_Axis', 'Thickness'], val=[32.,0.02])

        """
        for obj_name, fld_name, val in zip(obj_name, fld_name, val):
            objects = self.idf.idfobjects[obj_name]
            # Loop to handle multiple objects of the same object
            # TODO: multiple objects same name?
            for obj in objects:
                setattr(obj, fld_name, val)

    def set_output_path(self, output_path):
        """

        Parameters
        ----------
        output_path : str
            the desired path of the output files

        """
        self.output_path = output_path

    def get_output_path(self):
        """ get the output path

        Returns
        -------
        str

        """
        return self.output_path

    def run_idf(self):
        """ starts the simulations for the given idf parameters

        """
        # self.idf.saveas(self.run_filename)
        #
        # cmd = "energyplus "
        # if self.output_path:
        #     cmd += " -d " + self.output_path
        # cmd += " " + self.run_filename
        # os.system(cmd)
        # self.idf.run(weather="/mnt/c/EnergyPlusV9-1-0/WeatherData/USA_"
        # TODO: weather file path will be required per run or at least list them to choose
        #  , of course people won't simulate with any weather file :D
        self.idf.run(weather="C:/EnergyPlusV9-1-0/WeatherData/USA_"
                             "CA_San.Francisco.Intl.AP.724940_TMY3.epw", output_directory=self.output_path)

    def get_results(self):
        """ returns the output:variable data with the simulation values in a dictionary

        Returns
        -------
        dict

        """
        path_to_eso = self.output_path + '/eplusout.eso'
        dd = eso.read_from_path(path_to_eso)

        return dd.get_vars()
