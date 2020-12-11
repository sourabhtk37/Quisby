## Add a benchmark

 `mkdir quisby/benchmarks/<benchmark_name>`

 `cd quisby/benchmarks/<benchmark_name>`

 `touch extract.py graph.py summary.py comparison.py`

#### extract.py

 `def extract_<benchmark_name>_data(path)`

#### graph.py

 `def graph_<benchmark_name>_data(spreadsheetId, test_name)`

#### summary.py

 `def create_summary_<benchmark_name>_data(results)`

returns a lists of list, which each sublist represents a row in spreadsheet.

#### comparison.py

 `def compare_<benchmark_name>_results(spreadsheets, test_name)`

#### quisby.py

Add a text block:

```
elif test_name == "<benchmark_name>":
    results += extract_<benchmark_name>_result(data)
```
