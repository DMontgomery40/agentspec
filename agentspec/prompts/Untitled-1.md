  UW PICO 5.09                                                                                        File: /Users/davidmontgomery/.serena/serena_config.yml                                                                                           

# Added on 23.08.2025
# Advanced configuration option allowing to configure language server implementation specific options. Maps the language
# (same entry as in project.yml) to the options.
# Have a look at the docstring of the constructors of the LS implementations within solidlsp (e.g., for C# or PHP) to see which options are available.
# No documentation on options means no options are available.
# 

tool_timeout: 240
# timeout, in seconds, after which tool executions are terminated

excluded_tools: []
# list of tools to be globally excluded

included_optional_tools:
  - prepare_for_new_conversation
  - read_file
  - execute_shell_command
  - delete_lines
  - insert_at_line   
  - replace_lines
  - replace_regex
  - switch_modes
  - summarize_changes
  - create_text_file
# MANAGED BY SERENA, KEEP AT THE BOTTOM OF THE YAML AND DON'T EDIT WITHOUT NEED
# The list of registered projects.
# To add a project, within a chat, simply ask Serena to "activate the project /path/to/project" or,
# if the project was previously added, "activate the project <project name>".
# By default, the project's name will be the name of the directory containing the project, but you may change it
# by editing the (auto-generated) project configuration file `/path/project/project/.serena/project.yml` file.
# If you want to maintain full control of the project configuration, create the project.yml file manually and then
# instruct Serena to activate the project by its path for first-time activation.
# NOTE: Make sure there are no name collisions in the names of registered projects.
projects:
- /Users/davidmontgomery/agentspec

^G Get Help                              ^O WriteOut                              ^R Read File                             ^Y Prev Pg                               ^K Cut Text                              ^C Cur Pos                               
^X Exit                                  ^J Justify                               ^W Where is                              ^V Next Pg                               ^U UnCut Text                            ^T To Spell                              