# Quisby 

###### (Unoffical name) Quisby: An idler; one who does not or will not work. (noun)

Quisby is a tool to provide first view into the results from various benchmarks such as linpack, streams, fio etc. It doesn't aim to replace existing data viz tool but rather to provide a simplified view to the data with basic metric to understand the benchmark results from a higher level view. For detailed view, there are other tools such as pbench-dashboard, js-charts etc at hand.

Bechmarks currently supported:

|   Benchmark   |   Source data  |
|---|---|
| linpack | Benchmark result     |
| streams | Summary result       |
| uperf   | Summary csv result   |
| specjbb | Benchmark result     |
| pig     | Benchmark  result    |
| hammerDB| Benchmark  result    |
| fio     | pbench result        |
| autohpl | Summary  result      |
| aim     | Benchmark  result    |
| etcd    | pbench  result       |
| reboot  | Benchmark  result    |
| speccpu | Benchmark  result    |


### What it does

It extracts data from benchmark results file or summary results produced by wrapper benchmark programs and move that results to Google Sheet via sheets API V4. 


### Executable creation
pyinstaller --noconfirm --log-level=INFO -p quisby/ quisby.py

This command creates quisby executable. It binds all the dependencies into a file, making it easy to use.

## Prerequisites to run quisby executable

1. A google service account credentials(credentials.json) to hit various google APIs. 
2. Create a folder ~/.config/quisby/ if it doesn't exist. 
3. Copy credentials.json to the created folder.
4. Copy example.ini file to ~/.config/quisby/config.ini.

test_name(Name of test)                        
test_path( Path to test results directory )                        
results_location( Path to results_location file )                  
system_name( Mention cloud/baremetal system )
spreadsheetId( Mention spreadsheet ID if exists, otherwise quisby creates a new one for you ) 
users( Mention the users you need to give access too. Example - abc@gmail.com,xyz@gmail.com )                                

# How to run quisby

1. Extract the tar to the executable
2. Fill out the fields in config.ini file.
3. Run ./quisby.app 


### Run quisby using pip
```bash
$ 
```
$ pip install quisby

``` 
test: results_linpack
</path/to/results>
...
test: pbench_fio
<http url with results>
...
```

Then you can run
```bash
$ quisby process --os-type <add-here> --os-release <add-here> --cloud-type <add-here>  location_file`
```
For more information on options, run:

```bash
$ quisby -h
```

*That's it. It will return a google sheet. Visit the google sheet page and you will see a newly created spreadsheet with the data populated and graphed.*

### Comparison

If you want to compare two different OS release of similar system type then there are scripts that will help you to create a spreadsheet for the same. 

and then run:

```bash
quisby compare --test-name <benchmark-name-(optional)>  --spreadsheets <spreadsheet1,spreadsheet2>
```
and it would return a newly created spreadsheet with the comparison data.

## Development 

#Clone the repo
git clone git@github.com:sousinha1997/quisby.git

# Installation
source ./install.sh
(optional, for configuring aws and/or azure cli)
source ./install -aws -azure

## Contributing
Create issues and create a seperate feature branch to work on it. Push the changes to your clone repo and then create a pull request to the master branch of the origin repo.
