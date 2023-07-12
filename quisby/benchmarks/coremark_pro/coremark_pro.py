


""" Custom key to sort the data base don instance name """
def custom_key(item):
    if item[1][0] == "localhost":
        instance_type = item[1][0]
        return (instance_type)
    else:
        instance_type = item[1][0].split("-")[0]
        instance_number = int(item[1][0].split('-')[-1])
        return (instance_type, instance_number)

def create_summary_coremark_pro_data(results,OS_RELEASE):
    final_results = []
    multi_iter = [["Multi Iterations"],["System name", "Score"]]
    single_iter = [["Single Iterations"],["System name", "Score"]]
    # Sort data based on instance name
    sorted_data = sorted(results, key=custom_key)
    # Add summary data
    for item in sorted_data:
        for index in range(3, len(item)):
            multi_iter.append([item[1][0],item[index][1]])
            single_iter.append([item[1][0],item[index][2]])
            #final_results += item
    final_results += [[""]]
    final_results += multi_iter
    final_results += [[""]]
    final_results +=single_iter
    return final_results

def extract_coremark_pro_data(path, system_name, OS_RELEASE):
    """"""
    results = []
    processed_data =[]

    # Extract data from file
    try:
        if path.endswith(".csv"):
            with open(path) as file:
                coremark_results = file.readlines()
        else:
            return None
    except Exception as exc:
        print(str(exc))
        return None

    for index, data in enumerate(coremark_results):
        coremark_results[index] = data.strip("\n").split(":")

    # Format the data
    iteration = 1
    for row in coremark_results:
        if "Test" in row:
            processed_data.append([""])
            processed_data.append([system_name])
            processed_data.append([row[0], row[1], row[2]])
        elif "Score" in row:
            processed_data.append(["Score", row[1], row[2]])
    results.append(processed_data)
    return results
