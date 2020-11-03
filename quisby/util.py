def combine_two_array_alternating(results, value, ele):
    for list1, list2 in zip(value, ele):
        row = [None] * (len(list1[1:]) + len(list2[1:]))
        row[::2] = list1[1:]
        row[1::2] = list2[1:]
        results.append([list1[0]] + row)

    return results
