import os
from eppy.modeleditor import IDF
from eppy.idf_helpers import getidfobjectlist
from collections import OrderedDict
from EPinterface.esoReader import esoreader as eso
import sysconfig
import os

platform = sysconfig.get_platform()
install_dir = ''
output = None


class EnergyPlusHelper:
    """ A class for the EnergyPlus communicator
    """

    def __init__(self,
                 idf_path,
                 output_path,
                 weather_path,
                 idd_path=None,
                 ep_exe=None
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
        global platform, install_dir
        if not ep_exe:
            if "win" in platform:
                install_dir = "C:/EnergyPlus"
            elif "linux" in platform:
                homedir = os.path.expanduser("~")
                install_dir = os.path.join(homedir, "EnergyPlus")
            elif "mac" in platform:
                install_dir = ""
        else:
            install_dir = ep_exe
        self.idf_path = idf_path
        self.idd_path = idd_path or os.path.join(install_dir, "Energy+.idd")
        # TODO: handle the weather file path, for testing I'm using random one
        # wpath = os.path.join(install_dir, "WeatherData", "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
        wpath = os.path.join(install_dir, "WeatherData", "/mnt/D/F/uniopt/uniopt-server/IND_New.Delhi.421820_ISHRAE.epw")
        self.weather_path = weather_path or wpath
        self.output_path = output_path
        self.run_filename = "in.idf"
        IDF.setiddname(self.idd_path)
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
        objects  = self._sep_by_key(objects)
        objects = self._sep_by_name(objects)
        return objects

    def _sep_by_key(self, objects):
        frequency = set()
        for each in objects:
            if(not 'Output:' in each['key']):
                frequency.add(each['key'])

        seprated_by_freq = {}
        for mast_key in frequency:
            ind = []
            for val in objects:
                if 'key' in val:
                    if val['key'] == mast_key:
                        del val['key']
                        ind.append(val)
            if len(ind) == 1:
                ind = ind[0]
            seprated_by_freq[mast_key] = ind
        return seprated_by_freq

    def _sep_by_name(self, objects):
        final = {}
        for key in objects.items():
            if isinstance(key[1],list):
                master = {}
                name =""
                for item in key[1]:
                    name = ""
                    ind = {}
                    if 'Name' in item:
                        name = item.pop('Name')
                        ind = item
                    elif 'Zone_Name' in item:
                        name = item.pop('Zone_Name')
                        ind = item
                    master[name] = ind
                    
                final[key[0]] = master if name != "" else key[1]
            else:
                item = {}
                name = ""
                if 'Name' in key[1]:
                    ind = {}
                    name = key[1].pop('Name')
                    ind = key[1]
                    item[name] = ind
                final[key[0]] = key[1] if name=="" else item
        return final

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

    def get_field_val(self, obj_key, obj_name, fld_name):
        """ get multiple fields of multiple objects at once

        Parameters
        ----------
        obj_obj : list
            list of the objects keys
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
        for obj_key,obj_name, fld_name in zip(obj_key, obj_name, fld_name):
            objects = self.idf.idfobjects[obj_key]
            for each in objects:
                if each.Name == obj_name or len(objects) == 1:
                    fields.append(getattr(each, fld_name))
        return fields

    def set_field_val(self, obj_key, obj_name, fld_name, val):
        """ set multiple fields of multiple objects at once the usage of keys and name is
            due to the fact that some Objects share the same key but different names.
            If the object doesn't share a key with another object obj_name shall be empty.

        Parameters
        ----------
        obj_obj : list
            list of the objects keys
        obj_name : list
            list of the objects names
        fld_name : list
            list of fields names
        val : list
            list of values.

        Examples
        ----------
        >>> ep = EnergyPlusHelper(idf_path="path to idf",
        >>>                         idd_path="path to idd", weather_path="path to weather")
        >>> ep.set_field_val(obj_key=['BUILDING','Material'],obj_name=['','A1 - 1 IN STUCCO'],
                             fld_name=['North_Axis', 'Thickness'], val=[32.,0.02])
        """
        for obj_key,obj_name, fld_name, val in zip(obj_key, obj_name, fld_name, val):
            objects = self.idf.idfobjects[obj_key]
            for each in objects:
                if each.Name == obj_name or len(objects) == 1:
                    setattr(each, fld_name, val)


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
        global output
        self.idf.run(weather=self.weather_path, output_directory=self.output_path)
        output = self.get_results()

    def get_results(self):
        """ returns the output:variable data with the simulation values in a dictionary

        Returns
        -------
        dict

        """
        path_to_eso = self.output_path + '/eplusout.eso'
        dd = eso.read_from_path(path_to_eso)
        output = dd.get_vars()
        return output
    
    def get_output_var(self, to_track):
        """
        
        Parameters
        ----------
        to_track : list
            a list of parmeters to get from the results indexed by the defined structure
        
        Returns
        -------
        list
            list of lists contains each value returned

        Examples
        --------
        >>> get_output_var(to_track=[['RunPeriod','ROOM LIGHTS','Lights Electric Energy'],
                    ['RunPeriod','ZONE1AIR','Zone Ideal Loads Supply Air Total Heating Energy']])
        """
        global output
        vars = []
        for index in to_track:
            val = output
            for z in zip(range(0,len(index)-1),index):
                val = val[z[1]]
            for j in val:
                if j[0][1]==index[-1]:
                    vars.append(j[1])
        return vars
