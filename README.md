# plugin-updater
python script to automatically fetch and download paper/spigot plugins

this script takes a list of URLs from the `plugins.yml` file and scrapes each site automatically to find direct links to each latest plugin file. by default, the script moves all the current plugin files (i.e. all `.jar` files) in your plugin directory to an old plugins directory for safe keeping, in case there are and problems with the new versions, and downloads all the plugins into your plugins directory.

## installation
you will need python3 and pip3, install them using your package manager (i have absolutely no idea if this works outside of linux-based systems)
clone and navigate to the the repo and then install the script dependencies using:
```bash
pip3 install -r requirements.txt 
```
before running the updater, you need to set up `config.yml`.

## configuration
the configuration file (`plugins.yml`) uses the YAML syntax.
the script will automatically look for the `plugins.yml` file in the current working directory, however you can specify a different config file using the `--config` option.

the first section of the file is `config`, it currently contains two configurable options:
- `plugin-dir`: the directory where you want to install new plugins into
- `old-plugin-dir`: the directory where all old plugins will be moved to

the next section of the file is `downloads`, which contains information about where to fetch each file. currently, there are 3 supported fetch options: `bukkit` (from https://dev.bukkit.org/), `jenkins` (from jenkins CI) and `github` (from github releases). spigot resources are not currently supported (hard to scrape due to cloudflare).

for each of the options in `downloads`, there is a list of items. each item must contain a `url` property, which is the http(s) link to the resource. each item can also contain a list of `match` and `unmatch` properties:
- `match`: only grab the URLs which contain these keywords
- `unmatch`: from the list of matched URLs, throw out URLs that contain these keywords

each item needs to be one reference to one individual plugin. if something like a github release page includes multiple plugins (such is the case for essentialsx), you need to have multiple items with the same URL, and use `match` and `unmatch` accordingly.

view the included `plugins.yml` file for an example of the configuration i use for my server. you may need to experiment with `match` and `unmatch` to get the plugins you need.

## usage

to run plugin updater:
```bash
python3 plugin-updater.py
```

to view available options:
```bash
python3 plugin-updater.py --help
```
