from Utils import LocalUtils


def test_parse_line_to_log(lineData):
    print('testing test_parse_line_to_log start >>>>>>> ...')
    logItem = LocalUtils.parse_line_to_log(lineData)
    print('testing test_parse_line_to_log done <<<<<<<<<...\n')


if __name__ == '__main__':
    line = '05-05 16:12:59.703     0     0 E synx    : [sess: 7715329] invalid object handle 0'
    test_parse_line_to_log(line)
    line = '05-05 16:12:59.950  9252 26109 I Yolov5_Jian_JNI: [Profiling] Pre-processing: 75 ms'
    test_parse_line_to_log(line)
    line = '05-05 16:13:00.035  9252 26109 I QNNInterface: Done CovertToFloat'
    test_parse_line_to_log(line)
