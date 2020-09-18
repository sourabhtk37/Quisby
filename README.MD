## Quisby 
###### (Unoffical name) Quisby: An idler; one who does not or will not work. (noun)

Quisby is a tool to provide first view into the results from various benchmarks such as linpack, streams, fio etc. It doesn't aim to replace existing data viz tool but rather to provide a simplified view to the data with basic metric to understand the benchmark results from a higher level view. For detailed view, there are other tools such as pbench-dashboard, js-charts etc at hand.

Bechmarks currently supported:

|   Benchmark   |   Source data  |
|---|---|
| Linpack | Benchmark result     |
| Streams | Summary result |
| Uperf   | Summary result |

#### What it does
It extracts data from benchmark results file or summary results produced by wrapper benchmark programs and move that results to Google Sheet via sheets API V4. 

## Usage

### Prerequisite

#### Sheet credentials
One of the foremost thing required is access to Google sheets API V4. Follow the quickstart guide, till step-1 to get credentials.json file:

`https://developers.google.com/sheets/api/quickstart/python`

You will now have a credentials.json file. Copy the file to this project's directory. 

#### AWS credentials
Install boto3 to access aws API:

`pip install boto3`

If you're already using aws cli, you might probably have credentials in `~/.aws/credentials`. If not, please follow the `Configuration` in below link:

`https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html`

#### Azure credentials
Install azure cli tool and run:

`az login`

You will be good to go!

### Using the tool

#### Clone the repo

`git clone git@github.com:sourabhtk37/data-to-sheet.git`

#### config.py 
`config.py` is the only file you need to edit. Sample example have been provided in the file. 

#### reduce_results.py
This is the main driver program that needs to be called once you have edited `config.py` file accordingly. It takes in an input file with list of location to the test results.

`python reduce_results.py test_locations`

*That's it. It will return a google sheet. Visit the google sheet page and you will see a newly created spreadsheet with the data populated and graphed.*

## Contributing
Create issues and create a seperate feature branch to work on it. Push the changes to your clone repo and then create a pull request to the master branch of the origin repo.