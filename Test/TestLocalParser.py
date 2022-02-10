import re

from Utils.LocalUtils import parse_android_studio_logLine_to_log, check_log_types

filename = 'C:/test/logs_androidStudio.txt'
file2 = 'C:/test/logs_UI_thread_error.txt'
res = check_log_types(file2)

str = '20201211'
print(str.isalnum())
