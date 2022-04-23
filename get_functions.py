import sys
from elftools.elf.elffile import ELFFile

class DWARFData:
    def __init__(self, filename):
        self.filename = filename
        self.data = {
            "types": {},
            "typedefs": {},
            "functions": {}
        }
        self.process_file()

    def process_file(self):
        print('Processing file:', self.filename)
        with open(self.filename, 'rb') as f:
            elffile = ELFFile(f)

            if not elffile.has_dwarf_info():
                raise Exception(f"File has no DWARF info: {self.filename}")

            dwarfinfo = elffile.get_dwarf_info()
            for CU in dwarfinfo.iter_CUs():
                top_DIE = CU.get_top_DIE()

                self.recursively_process_dwarfinfo(top_DIE)

    def recursively_process_dwarfinfo(self, die, stack=None):
        """
        Recursively process dwarfinfo and load the function data into self.data
        """

        if die.tag == "DW_TAG_subprogram":
            name = die.attributes["DW_AT_name"].value.decode("utf-8")
            return_type_id = die.attributes["DW_AT_type"].value
            self.data["functions"][name] = {
                "return_type_id": return_type_id,
                "params": []
            }
            # children of this tag that are DW_TAG_formal_parameter need to know which function to assign themselves to
            stack=name
        elif die.tag == "DW_TAG_base_type":
            name = die.attributes["DW_AT_name"].value.decode("utf-8")
            self.data["types"][die.offset] = name
        elif die.tag == "DW_TAG_typedef":
            name = die.attributes["DW_AT_name"].value.decode("utf-8")
            type_id = die.attributes["DW_AT_type"].value
            self.data["typedefs"][die.offset] = {
                "name": name,
                "type_id": type_id
            }
        elif die.tag == "DW_TAG_formal_parameter":
            name = die.attributes["DW_AT_name"].value.decode("utf-8")
            type_id = die.attributes["DW_AT_type"].value
            self.data["functions"][stack]["params"].append({
                "name": name,
                "type": type_id
            })
        else:
            pass

        for child in die.iter_children():
            self.recursively_process_dwarfinfo(child, stack)

    def get_type_name(self, type_id):
        if type_id in self.data["types"]:
            return self.data["types"][type_id]
        if type_id in self.data["typedefs"]:
            return self.data["typedefs"][type_id]["name"]
        raise Exception("no type")

    def prettyprint_function(self, fn_name):
        fn_info = self.data["functions"][fn_name]
        return_type_name = self.get_type_name(fn_info["return_type_id"])
        params = ", ".join([f"{dd.get_type_name(param['type'])} {param['name']}" for param in fn_info["params"]])
        print(f"{return_type_name} {fn_name}({params});")

    def get_functions(self):
        return self.data["functions"].keys()

if __name__ == '__main__':
    dd = DWARFData(sys.argv[1])

    for fn in dd.get_functions():
        dd.prettyprint_function(fn)
