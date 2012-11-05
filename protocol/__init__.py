import yapsy

class manager(yapsy.PluginManager):
	def __init__(self, 
				 categories_filter={"Default":IPlugin}, 
				 directories_list=None, 
				 plugin_info_ext="mpb-protocol",
                 apiversion):
		"""
		Initialize the mapping of the categories and set the list of
		directories where plugins may be. This can also be set by
		direct call the methods: 
		
		- ``setCategoriesFilter`` for ``categories_filter``
		- ``setPluginPlaces`` for ``directories_list``
		- ``setPluginInfoExtension`` for ``plugin_info_ext``

		You may look at these function's documentation for the meaning
		of each corresponding arguments.
		"""
        self.APIversion = apiversion
		self.setPluginInfoClass(PluginInfo)
		self.setCategoriesFilter(categories_filter)		
		self.setPluginPlaces(directories_list)
		self.setPluginInfoExtension(plugin_info_ext)

	def _getPluginNameAndModuleFromStream(self, infoFileObject, candidate_infofile="<buffered info>"):
		"""
		Extract the name and module of a plugin from the
		content of the info file that describes it and which
		is stored in infoFileObject.

		.. note:: Prefer using ``_gatherCorePluginInfo``
		instead, whenever possible...
                
                .. warning:: ``infoFileObject`` must be a file-like
                object: either an opened file for instance or a string
                buffer wrapped in a StringIO instance as another
                example.

                .. note:: ``candidate_infofile`` must be provided
                whenever possible to get better error messages.
                
		Return a 3-uple with the name of the plugin, its
		module and the config_parser used to gather the core
		data *in a tuple*, if the required info could be
		localised, else return ``(None,None,None)``.
		
		.. note:: This is supposed to be used internally by subclasses
		    and decorators.
                """
		# parse the information buffer to get info about the plugin
		config_parser = configparser.SafeConfigParser()
		try:
			config_parser.readfp(infoFileObject)
		except Exception as e:
			logging.warning("Could not parse the plugin file '%s' (exception raised was '%s')" % (candidate_infofile,e))
			return (None, None, None)
		# check if the basic info is available
		if not config_parser.has_section("Core"):
			logging.warning("Plugin info file has no 'Core' section (in '%s')" % candidate_infofile)					
			return (None, None, None)
		if not config_parser.has_option("Core","Name") or not config_parser.has_option("Core","Module") or not config_parser.has_option("Core", "APIversion"):
			logging.warning("Plugin info file has no 'Name', 'Module', or 'APIversion' section (in '%s')" % candidate_infofile)
			return (None, None, None)
        # check if api version matches
        if not config_parser.get("Core", "APIversion") == self.APIversion:
            logging.warning("API version does not match (in '%s')" % candidate_infofile)
            return (None, None, None)
		# check that the given name is valid
		name = config_parser.get("Core", "Name")
		name = name.strip()
		if PLUGIN_NAME_FORBIDEN_STRING in name:
			logging.warning("Plugin name contains forbiden character: %s (in '%s')" % (PLUGIN_NAME_FORBIDEN_STRING,
																				   candidate_infofile))
			return (None, None, None)
		return (name,config_parser.get("Core", "Module"), config_parser)
