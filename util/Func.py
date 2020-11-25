def show_error(func_name, res):
    if res.error_code != '0':
        print('%s respond error_code: %s' % (func_name, res.error_code))
        print('%s respond  error_msg: %s' % (func_name, res.error_msg))


def get_target_stock(path):
    result = []
    with open(path, "r") as finput:
        for line in finput:
            if "#" not in line and len(line.strip()) > 0:
                result.append(line.strip().split(","))

    return result




if __name__ == "__main__":

    path = "../resource/target_stock.dat"
    print(get_target_stock(path))