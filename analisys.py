import pandas


def get_list_os():
    with open('os_phones.json', 'r') as fd:
        list_os = fd.read().split('"')
        for item in list_os:
            if item == '':
                list_os.remove(item)
    return list_os


def count_grouped_os(list_os):
    temp = pandas.DataFrame({ 'Name': list_os })
    array_counts_not_sorted = temp.groupby('Name', sort=True)['Name'].count()
    return array_counts_not_sorted.sort_values(ascending=False).to_frame()
    

def save_data(histogram):
    with open('123.txt', 'w') as fd:
        # without the table header
        fd.write(histogram[38:])


def main():
    list_os = get_list_os()
    histogram_os = count_grouped_os(list_os)
    save_data(histogram_os.to_string())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)