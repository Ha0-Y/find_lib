from elftools.elf.elffile import ELFFile
import os


class Match:

    def __init__(self, exe: str, libp: str):
        self.exe = exe
        if libp[-1] != "/":
            libp += "/"
        self.libp = libp

    def get_lib_names(self) -> list:
        all_libs = []
        try:
            with open(self.exe, "rb") as f:
                elf = ELFFile(f)
                dynamic_section = elf.get_section_by_name(".dynamic")
                strtab_section = elf.get_section(dynamic_section["sh_link"])

                for tag in dynamic_section.iter_tags():
                    # 判断条目的标签类型是否为DT_NEEDED（指定的动态链接库）
                    if tag.entry.d_tag == "DT_NEEDED":
                        # 获取动态链接库的名称字符串在字符串表中的偏移量
                        str_offset = tag.entry.d_val
                        # 获取动态链接库的名称字符串
                        library_name = strtab_section.get_string(str_offset)
                        # 打印动态链接库的名称
                        all_libs.append(library_name)
        except FileExistsError:
            print("[-] file not exists")
        return all_libs

    def match(self, function) -> None:
        found = False
        names = self.get_lib_names()
        lib_paths = [self.libp + name for name in names]
        # maybe change
        def get_func_name(name: str) -> str:
            if '@' in name:
                idx = name.index("@")
            else: 
                idx = len(name)
            # print(name[:idx])
            return name[:idx]

        for so_file_path in lib_paths:
            with os.popen(f"nm -D {so_file_path}") as f:
                # 创建ELFFile对象
                for lines in f:
                    line = lines.split()
                    if len(line) == 2:
                        if line[0] == "T" and function == get_func_name(line[-1]):
                            found = True
                            print(f"[+] {function} is defined in {so_file_path}")
                    elif len(line) == 3:
                        if line[1] == "T" and function == get_func_name(line[-1]):
                            found = True
                            print(f"[+] {function} is defined in {so_file_path}")
        if not found:
            print(f"[-] {function} cannot find!")
    
    # def match(self, function) -> None:
    #     from collections import defaultdict
    #     names = self.get_lib_names()
    #     lib_paths = [self.libp + name for name in names]
    #     # print(lib_paths)
    #     # lib->func
    #     export_functions = defaultdict(list)
    #     for so_file_path in lib_paths:
    #         with open(so_file_path, "rb") as f:
    #             # 创建ELFFile对象
    #             elf = ELFFile(f)

    #             # 获取动态链接库导出符号表（Export Symbol Table）
    #             export_table = elf.get_section_by_name('.dynsym')

    #             # 获取动态链接库字符串表（String Table）
    #             str_table = elf.get_section_by_name('.dynstr')

    #             # 遍历导出符号表中的符号条目
    #             for symbol in export_table.iter_symbols():
    #                 # 判断符号类型是否为函数符号（Text）
    #                 if symbol['st_info']['type'] == 'STT_FUNC':
    #                     # name
    #                     symbol_name = symbol.name

    #                     export_functions[symbol_name].append(so_file_path)

    #     for k in export_functions.keys():
    #         if k == function:
    #             print(f"\033[31m{k}\033[0m is defined in {export_functions[k]}")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-E", "--elf", type=str, help="ELF path")
    parser.add_argument("-L", "--lib", type=str, help="lib path")
    parser.add_argument("-F", "--function", type=str, help="function name")

    args = parser.parse_args()

    m = Match(args.elf, args.lib)
    m.match(args.function)
