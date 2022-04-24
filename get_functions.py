import sys
from elftools.elf.elffile import ELFFile
import graphlib

class DWARFData:
    def __init__(self, filename):
        self.filename = filename
        self.data = {
            "types": {},
            "typedefs": {},
            "functions": {}
        }
        # holds a mapping of names->ids, for convenience
        self.names = {
            "types": {},
            "typedefs": {}
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
            self.names["types"][name] = die.offset
        elif die.tag == "DW_TAG_typedef":
            name = die.attributes["DW_AT_name"].value.decode("utf-8")
            type_id = die.attributes["DW_AT_type"].value
            self.data["typedefs"][die.offset] = {
                "name": name,
                "reference_type_id": type_id
            }
            self.names["typedefs"][name] = die.offset
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

    def is_type(self, type_name):
        return type_name in self.names["types"]

    def is_typedef(self, type_name):
        return type_name in self.names["typedefs"]

    def get_typedef_reference(self, type_name):
        type_id = self.names["typedefs"][type_name]
        reference_id = self.data["typedefs"][type_id]["reference_type_id"]
        reference_name = self.get_type_name(reference_id)
        return reference_name

    def get_return_type_name(self, fn_name):
        fn_info = self.data["functions"][fn_name]
        return self.get_type_name(fn_info["return_type_id"])

    def get_function_param_types(self, fn_name):
        fn_info = self.data["functions"][fn_name]
        return [self.get_type_name(param['type']) for param in fn_info["params"]]

    def get_typedef_string(self, type_name):
        refrence_type = self.get_typedef_reference(type_name)
        return f"typedef {refrence_type} {type_name};"

    def get_function_string(self, fn_name):
        fn_info = self.data["functions"][fn_name]
        return_type_name = self.get_return_type_name(fn_name)
        params = ", ".join([f"{self.get_type_name(param['type'])} {param['name']}" for param in fn_info["params"]])
        return f"{return_type_name} {fn_name}({params});"

    def get_list_of_functions(self):
        return self.data["functions"].keys()

    def calc_typedef_dag(self):
        params = set()
        for fn in self.get_list_of_functions():
            for type_name in self.get_function_param_types(fn):
                params.add(type_name)
            params.add(self.get_return_type_name(fn))

        # create a dag of all typedefs we can include them in the correct order
        graph = {}
        while params:
            # we only need items the the dag that are typedefs
            params = set(type_name for type_name in params if self.is_typedef(type_name))
            for type_name in params:
                referenced_type = self.get_typedef_reference(type_name)
                graph[type_name] = { referenced_type }

            for type_name, refernece_name_set in graph.items():
                refernece_name = list(refernece_name_set)[0]
                # once we add the next typedef, remove it from our list
                if type_name in params:
                    params.remove(type_name)
                # if the refereced type is also a typedef, add it our list
                if self.is_typedef(refernece_name):
                    params.add(refernece_name)

        # compute DAG
        dag = tuple(graphlib.TopologicalSorter(graph).static_order())
        return (type_name for type_name in dag if self.is_typedef(type_name))

def main(filename):
    dd = DWARFData(filename)

    # print typedefs in order
    for type_name in dd.calc_typedef_dag():
        print(dd.get_typedef_string(type_name))

    # get a set of all used types, so we can figure out what typedefs we need
    for fn in dd.get_list_of_functions():
        print(dd.get_function_string(fn))

if __name__ == '__main__':
    main(sys.argv[1])
