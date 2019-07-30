# from __future__ import print_function
from WBT.whitebox_tools import WhiteboxTools, to_camelcase
wbt = WhiteboxTools()

"""
This script is just used to automatically generate the documentation for each
of the plugin tools in the WhiteboxTools User Manual. It should be run each time new
tools are added to WhiteboxTools.exe and before a public release.
"""
import os
from os import path
import re
import json
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


def to_camelcase(name):
    '''
    Convert snake_case name to CamelCase name
    '''
    return ''.join(x.title() for x in name.split('_'))


wbt = WhiteboxTools()
# Get the root directory containing the WhiteboxTools repo
root_dir = path.dirname(path.dirname(path.abspath(__file__)))
# Set the directory containing the whitebox_tools.exe file
# wbt.exe_path = path.join(root_dir, "target/release/")
# wbt.exe_path = r'C:/Desktop/whitebox-tools-master/target/release/'
# wbt.ext_path = r'../target/release/'

tool_dir = "C:/Desktop/whitebox-tools-master/src/tools/"
# in_files = []
# for dirpath, dirnames, filenames in os.walk(tool_dir):
#     for filename in [f for f in filenames if f.endswith(".rs")]:
#         in_files.append(os.path.join(dirpath, filename))

# toolList = []
# for filepath in in_files:
#     with open(filepath) as f:
#         for line in f:
#             if line.startswith("pub struct"):
#                 toolname = line.replace("pub struct", "").replace(
#                     "{", "").replace("\n", "").strip()
#                 toolList.append(toolname)

# toolAuthors = {}
# createdDates = {}
# tool_help_dict = {}
# num_help_files = 0

# for filepath in in_files:
#     with open(filepath) as f:
#         toolAuthor = "Unknown"
#         createdDate = "Unknown"
#         toolname = "Unknown"
#         docs = []
#         for line in f:
#             if line.startswith("///"):
#                 docs.append(line.replace("///", "").replace("\n", "").strip())
#             elif line.startswith("Authors:"):
#                 toolAuthor = line.replace("Authors:", "").strip()
#             elif line.startswith("Created:"):
#                 createdDate = line.replace("Created:", "").strip()
#             elif line.startswith("pub struct") and len(docs) > 0:
#                 num_help_files += 1
#                 toolname = line.replace("pub struct", "").replace(
#                     "{", "").replace("\n", "").strip()

#                 helpstring = ""
#                 for l in docs:
#                     l = l.replace(
#                         "# See Also:", "*See Also*:\n").replace("# See Also", "*See Also*:\n").replace("# References", "*References*:\n").replace("# Reference", "*Reference*:\n").replace("# Algorithm Description", "*Algorithm Description*:\n").replace("# Warning", "*Warning*:\n")
#                     helpstring += l + "\n"
#                 found = re.findall(r'`(.+?)`', helpstring)
#                 toolsInDoc = set()
#                 for f in found:
#                     toolsInDoc.add(f)

#                 for f in toolsInDoc:
#                     for t in toolList:
#                         if f == t:
#                             tb = wbt.toolbox(t)
#                             nm = tb.replace("/", "").replace(" ",
#                                                              "").replace("\n", "")
#                             nm = camel_to_snake(nm)
#                             if nm == "li_dar_tools":
#                                 nm = "lidar_tools"
#                             j = "[**{}**](./{}.html#{})".format(f,
#                                                                 nm, f.lower())
#                             # print(toolname, ": ", j)
#                             helpstring = helpstring.replace(
#                                 "`{}`".format(f), j)
#                             break
#                 tool_help_dict[camel_to_snake(toolname)] = helpstring
#             elif line.startswith("pub struct"):
#                 toolname = line.replace("pub struct", "").replace(
#                     "{", "").replace("\n", "").strip()

#         if toolname != "Unknown":
#             toolAuthors[toolname.lower()] = toolAuthor
#             createdDates[toolname.lower()] = createdDate

# toolboxes = wbt.toolbox('')
# print("toolboxes: \n" + toolboxes)
# print("_______________________________________________________________________________________________________\n")
# tb_set = set()
# tool_set = set()

# for tb in toolboxes.split('\n'):
#     print("*" + tb + "*")
#     if tb.strip():
#         tb_set.add(tb.strip().split(':')[1].strip())
#         tool_set.add(tb.strip().split(':')[0].strip())
# print(tb_set)
# sorted(tb_set)
# print(tb_set)
# toolbox_list = ['Geomorphometric Analysis', 'Stream Network Analysis', 'Image Processing Tools/Filters', 'GIS Analysis/Distance Tools', 'Image Processing Tools/Image Enhancement', 'Math and Stats Tools', 'Image Processing Tools', 'Data Tools', 'LiDAR Tools', 'GIS Analysis', 'GIS Analysis/Patch Shape Tools', 'Hydrological Analysis', 'GIS Analysis/Overlay Tools']
# index = 0
# toolAndToolbox = [[] for i in range(len(toolboxes))]
# print(str(toolAndToolbox))
# toolboxAndTools = [[] for i in range(len(tb_set))]
# print(str(toolboxAndTools))
# for tb in toolboxes.split('\n'):
#     print("*" + tb + "*")
#     if tb.strip():
#         toolAndToolbox[index].append(tb.strip().split(':')[0].strip())    #tool
#         toolAndToolbox[index].append(tb.strip().split(':')[1].strip())    #toolbox
#         index = index + 1
# print(str(toolAndToolbox))

# index = 0
# toolboxAndTools = [[] for i in range(len(tb_set))]
# print(str(toolboxAndTools))


# print(str(toolboxAndTools))
# print("_______________________________________________________________________________________________________\n")
# print(tb_set)
# print("_______________________________________________________________________________________________________\n")
# print(toolboxes)


# tb_dict = {}
# for tb in sorted(tb_set):
#     tb_dict[tb] = []

descriptionList = []
tools = wbt.list_tools()
print("tools: " + str(tools))
tools2 = tools.items()

for t in tools2:
    print("\t" + str(t))   
    print("\t\t" + t[0])
    print("\t\t" + t[1])
    description = t[1]
    descriptionList.append(description)

print("descriptionList: " + str(descriptionList))
#     if t.strip() and "Available Tools" not in t:
#         tool = t.strip().split(":")[0]
#         description = t.strip().split(":")[1].strip().rstrip('.')
# for tool, description in tools.items():
#     toolbox = wbt.toolbox(tool).strip()

#     if tool in tool_help_dict:
#         description = tool_help_dict[tool]

#     tool = to_camelcase(tool)

#     tool_help = wbt.tool_help(tool)
#     flag = False
#     example = ''
#     for v in tool_help.split('\n'):
#         if flag:
#             example += v + "\n"
#         if "Example usage:" in v:
#             flag = True

#     if len(example) > 65:
#         a = example.split('-')
#         example = ''
#         count = 0
#         b = 0
#         for v in a:
#             if v.strip():
#                 if count + len(v) < 65:
#                     if not v.startswith('>>'):
#                         example += "-{} ".format(v.strip())
#                         count += len(v) + 2
#                     else:
#                         example += "{} ".format(v.strip())
#                         count = len(v) + 1

#                 else:
#                     example += "^\n-{} ".format(v.strip())
#                     count = len(v) + 1
#             else:
#                 a[b + 1] = "-" + a[b + 1]

#             b += 1

#     doc_str = ""
#     parameters = wbt.tool_parameters(tool)
#     j = json.loads(parameters)
#     param_num = 0

#     tool_snaked = camel_to_snake(tool)
#     if tool_snaked == "and":
#         tool_snaked = "And"
#     if tool_snaked == "or":
#         tool_snaked = "Or"
#     if tool_snaked == "not":
#         tool_snaked = "Not"

#     fn_def = "wbt.{}(".format(tool_snaked)
#     default_params = []
#     arg_append_str = ""
#     # parameter_num = 1

#     for p in j['parameters']:
#         st = r"{}"
#         st_val = '        '
#         if param_num == 0:
#             st_val = ''
#         param_num += 1

#         json_str = json.dumps(
#             p, sort_keys=True, indent=2, separators=(',', ': '))

#         flag_str = ""
#         for v in p['flags']:
#             flag_str += "{}, ".format(v.replace('--', '-\-'))
#         flag_str = flag_str.rstrip(', ')
#         desc = p['description'].strip().rstrip('.')
#         if len(desc) > 80:
#             a = desc.split(' ')
#             desc = ''
#             count = 0
#             for v in a:
#                 desc += "{} ".format(v)
#                 count += len(v) + 1
#                 # if count + len(v) < 80:
#                 #     desc += "{} ".format(v)
#                 #     count += len(v) + 1
#                 # else:
#                 #     desc += "\n{}{} ".format(' ' * 20, v)
#                 #     count = len(v) + 1

#         doc_str += "{}{}| {}\n".format(flag_str, ' ' * (20 - len(flag_str)),
#                                        desc)

#         flag = p['flags'][len(p['flags']) - 1].replace('-', '')
#         if flag == "class":
#             flag = "cls"
#         if flag == "input":
#             flag = "i"

#         pt = p['parameter_type']
#         if 'Boolean' in pt:
#             if p['default_value'] != None and p['default_value'] != 'false':
#                 default_params.append(
#                     "{}=True, ".format(camel_to_snake(flag)))
#             else:
#                 default_params.append(
#                     "{}=False, ".format(camel_to_snake(flag)))

#             arg_append_str += "{}if {}: args.append(\"{}\")\n".format(
#                 st_val, camel_to_snake(flag), p['flags'][len(p['flags']) - 1])
#         else:
#             if p['default_value'] != None:
#                 if p['default_value'].replace('.', '', 1).isdigit():
#                     default_params.append("{}={}, ".format(
#                         camel_to_snake(flag), p['default_value']))
#                 else:
#                     default_params.append("{}=\"{}\", ".format(
#                         camel_to_snake(flag), p['default_value']))

#                 arg_append_str += "{}args.append(\"{}={}\".format({}))\n".format(
#                     st_val, p['flags'][len(p['flags']) - 1], st, camel_to_snake(flag))
#             else:
#                 if not p['optional']:
#                     # if parameter_num == 1:
#                     #     fn_def += "{}, ".format(camel_to_snake(flag))
#                     # else:
#                     fn_def += "\n    {}, ".format(camel_to_snake(flag))

#                     # parameter_num += 1

#                     arg_append_str += "{}args.append(\"{}='{}'\".format({}))\n".format(
#                         st_val, p['flags'][len(p['flags']) - 1], st, camel_to_snake(flag))
#                 else:
#                     default_params.append(
#                         "{}=None, ".format(camel_to_snake(flag)))
#                     arg_append_str += "{}if {} is not None: args.append(\"{}='{}'\".format({}))\n".format(
#                         st_val, flag, p['flags'][len(p['flags']) - 1], st, camel_to_snake(flag))

#                 # arg_append_str += "{}args.append(\"{}='{}'\".format({}))\n".format(
#                 #     st_val, p['flags'][len(p['flags']) - 1], st, camel_to_snake(flag))

    # for d in default_params:
    #     # if parameter_num == 1:
    #     #     fn_def += d
    #     # else:
    #     fn_def += '\n    ' + d

    #     # parameter_num += 1

    # fn_def += "\n    callback=default_callback\n)"

    # fn = """
# <a name="{}"></a>
# # {}

# {}

# *Parameters*:

# **Flag**            |  **Description**
# ------------------- | -------------------
# {}

# *Python function*:

# ```python
# {}
# ```

# *Command-line Interface*:

# ```
# {}
# ```

# [Source code on GitHub]({})

# *Author*: {}

# *Created*: {}
# """.format(tool, tool, description.strip(), doc_str, fn_def, example, wbt.view_code(tool), toolAuthors[tool.lower()], createdDates[tool.lower()])
#     tb_dict[toolbox].append((tool, fn))


# indexEntry = "1. [{}](available_tools/{}#{}): {} Found in *{}*.\n\n"
# toolEntryList = []

# out_dir = path.join(root_dir, "WhiteboxToolsUserManual/src/available_tools/")
# # if not os.path.exists(out_dir):
# #     os.mkdir(out_dir)
# for key, value in sorted(tb_dict.items()):
#     nm = key.replace("/", "").replace(" ", "")
#     nm = camel_to_snake(nm)
#     if nm == "li_dar_tools":
#         nm = "lidar_tools"
#     out_file = os.path.join(out_dir, "{}.md".format(nm))
#     print(out_file)
#     f = open(out_file, 'w')
#     f.write("# {}\n".format(key.replace("/", " &#8594; ")))

#     # table of contents
#     for v in sorted(value):
#         f.write("- [{}](#{})\n".format(v[0], v[0]))
#         description = tools[camel_to_snake(v[0])]
#         toolEntryList.append(indexEntry.format(v[0], out_file.replace(
#             out_dir, ""), v[0], description, key.replace("/", " &#8594; ")))

#     f.write("")

#     # contents
#     for v in sorted(value):
#         f.write("{}\n".format(v[1]))

#     f.close()

# out_file = os.path.join(out_dir.replace(
#     "available_tools/", ""), "tool_index.md")
# f = open(out_file, 'w')
# f.write("# Index of Tools\n\n")
# toolEntryList.sort()
# for value in toolEntryList:
#     f.write(value)

# f.close()

# print("Number of help files located: {}".format(num_help_files))
