import quisby.config as config

invalid_compare_list = ["pig"]


def merge_lists_alternately(results, list1, list2):
    merger_list = []

    merger_list.append(list1[0])
    for item1, item2 in zip(list1[1:], list2[1:]):
        merger_list.append(item1)
        merger_list.append(item2)
    
    results.append(merger_list)
    

    # row = [None] * (len(item1[1:]) + len(item2[1:]))
    # row[::2] = item1[1:]
    # row[1::2] = item2[1:]
    # results.append([item2[0]] + row)

    return results


def combine_two_array_alternating(results, value, ele):
    indexer = []

    for lindex, item1 in enumerate(value[0][1:]):
        for rindex, item2 in enumerate(ele[0][1:]):
            if item1.split("-", 1)[0] == item2.split("-", 1)[0]:
                indexer.append([lindex, rindex])
            elif config.test_name in invalid_compare_list:
                indexer.append([lindex, rindex])

    for list1, list2 in zip(value, ele):
        holder_list = []
        holder_list.append(list1[0])

        for index in indexer:
            holder_list.append(list1[index[0] + 1])
            holder_list.append(list2[index[1] + 1])

        results.append(holder_list)

    return results


def mk_int(str):
    str = str.strip()
    return int(str) if str else 1
