def show_error(func_name, res):
    if res.error_code != '0':
        print('%s respond error_code: %s' % (func_name, res.error_code))
        print('%s respond  error_msg: %s' % (func_name, res.error_msg))
