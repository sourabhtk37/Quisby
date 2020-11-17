## Quisby 

###### (Unoffical name) Quisby: An idler; one who does not or will not work. (noun)

Quisby is a tool to provide first view into the results from various benchmarks such as linpack, streams, fio etc. It doesn't aim to replace existing data viz tool but rather to provide a simplified view to the data with basic metric to understand the benchmark results from a higher level view. For detailed view, there are other tools such as pbench-dashboard, js-charts etc at hand.

Bechmarks currently supported:

|   Benchmark   |   Source data  |
|---|---|
| Linpack | Benchmark result     |
| Streams | Summary result |
| Uperf   | Summary csv result|
| specjbb | Benchmark result |
| pig     | Benchmark  result |
| hammerDB| Benchmark  result |
| fio     | pbench results      |

#### What it does

It extracts data from benchmark results file or summary results produced by wrapper benchmark programs and move that results to Google Sheet via sheets API V4. 

### Using the tool

#### Clone the repo

 `git clone git@github.com:sourabhtk37/data-to-sheet.git`

#### Installation

Run the install script as follows:

 `source ./install.sh`

#### config.py 

`config.py` is the only file you need to edit. Sample example have been provided in the file. 

#### quisby.py

This is the main driver program that will be called once you have edited `config.py` file accordingly. It takes in an input file with list of location to the test results.

The location file will look like:

``` 

tests: results_linpack
</path/to/results>
...
tests:pbench_fio
<http url with results>
...
```

 `quisby test_locations`

*That's it. It will return a google sheet. Visit the google sheet page and you will see a newly created spreadsheet with the data populated and graphed.*

### Comparison

If you want to compare two different OS release of similar system type then there are scripts that will help you to create a spreadsheet for the same. 

and then run:

 `quisby compare <benchmark-name> <spreadsheet1,spreadsheet2>`

and it would return a newly created spreadsheet with the comparison data.

## Contributing

Create issues and create a seperate feature branch to work on it. Push the changes to your clone repo and then create a pull request to the master branch of the origin repo.
