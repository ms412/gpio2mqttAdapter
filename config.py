
import yaml
import re

class config(object):
    """
Simple YAML configuration parser
"""

    def __init__(self, config = None):
        """
        Constructor, parses and stores the configuration
        """
        self.config=config
        
    def Open(self, filename):
  #      print "filename",filename
        handler = file(filename, 'r')
        self.config = yaml.load(handler,yaml.BaseLoader)
        handler.close()

    def get(self, section, key=None, default=None):
        """
        Retrieves a given section/key combination,
        if not existent it return a default value
        """
        try:
            if key is None:
                return self.config[section]
            else:
                return self.config[section][key]
        except:
            return default
        
    def printall(self):
        return self.config
    
    def keys(self, section):
                  
        return self.config[section].keys()
    

    def subsection(self, section, key=None, default=None):
        list = []
        try:
            if key is None:
                for key in self.config.keys():
                    return self.config[section]
            else:
                for item in self.config[section].keys():
                    if re.search(key, item, re.IGNORECASE):
                        list.append(self.config[section][item])
                return list
        except:
            return default
    
    def getSectionByRegex(self, regexkey):
        list = []
        result = False
        try:
            for item in self.config.keys():
                if re.search(regexkey, item, re.IGNORECASE):
                    list.append(self.config[item])
                    result = True
        
            if result == True:
                return list
            else:
                return result
        except:
            return False

  