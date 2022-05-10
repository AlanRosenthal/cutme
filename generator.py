
# int fn(int param, int param2);

class CGenerator():
    def __init__(self):
        self.data = {
            "name": "fn",
            "type": "int",
            "params": [
                {
                    "type": "uint32_t"
                },
                {
                    "type": "int8_t"
                }
            ]
        }


        self.mock_param_structs = ""
        self.fn_prototypes = ""

        self.generate_param_structs()
        self.generate_functions()
        self.output = f"""
#pragma once

enum {{
    MOCK_PARAM_IGNORE,
    MOCK_PARAM_CHECK
}} mock_param_e;

{self.mock_param_structs}

{self.fn_prototypes}
"""
    @property
    def get_fn_name(self):
        return self.data["name"]

    @property
    def get_fn_type(self):
        return self.data["type"]

    def generate_param_structs(self):
        struct_list = []
        for param_num in range(len(self.data["params"])):
            param = self.data["params"][param_num]
            param_name = f"mock_{self.get_fn_name}_param{param_num}"
            struct_definition_str = """struct {{
    {TYPE} value;
    enum mock_param_e mock_param;
}} {STRUCT_NAME};""".format(STRUCT_NAME=param_name, TYPE=param["type"])
            struct_list.append(struct_definition_str)

        self.mock_param_structs="\n\n".join(struct_list)

    def generate_functions(self):
        params_list = []
        for param_num in range(len(self.data["params"])):
            param = self.data["params"][param_num]
            param_name = f"mock_{self.get_fn_name}_param{param_num}"
            params_list.append(f"struct {param_name} param{param_num}")

        return_type = self.data["type"]
        params_list.append(f"{return_type} ret_value")
        param_str = ", ".join(params_list)
        self.fn_prototypes = f"{self.get_fn_type} {self.get_fn_name}({param_str});"


def main():
    # ret = data["return_type"]
    # fn_name = data["name"]
    # print(f"{ret} mock_{fn_name}();")

    c_gen = CGenerator()
    print(c_gen.output)
    # c_gen.print_mock_enums()
    # c_gen.print_params_prototypes()



if __name__ == "__main__":
    main()
