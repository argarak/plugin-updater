#!/usr/bin/env python3

import os
import yaml
import click
import signal
import shutil
import requests
from glob import glob
from time import sleep
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress

# pretty text in terminal
console = Console()

class Downloader:
  def __init__(self, config):
    self.downloads = []
    self.pluginDir = config["plugin-dir"]
    self.oldPluginDir = config["old-plugin-dir"]

  def matchAll(self, dls, link):
    for dl in dls:
      if "match" in link:
        if any([m in dl for m in link["match"]]):
          if "unmatch" in link:
            if any([not u in dl for u in link["unmatch"]]):
              yield dl
          else:
            yield dl
      else:
        yield dl

  def bukkit(self, link):
    page = requests.get(link["url"] + "/files/latest")
    self.downloads.append(page.url)

  def jenkins(self, link):
    page = requests.get(link["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    filelist = soup.find("table", {"class": "fileList"})
    results = filelist.findAll(lambda tag: tag.name == "a" and \
                               "href" in tag.attrs and \
                               not "fingerprint" in tag.attrs["href"] and \
                               not "view" in tag.attrs["href"])

    # get all download links
    dls = []
    for result in results:
      dls.append(result.attrs["href"])

    for matching in self.matchAll(dls, link):
      self.downloads.append(link["url"] + "/" + matching)

  def github(self, link):
    page = requests.get(link["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.findAll(lambda tag: tag.name == "a" and \
                           "href" in tag.attrs and \
                           "/releases/download/" in tag.attrs["href"])

    # get all download links
    dls = []
    for result in results:
      dls.append(result.attrs["href"])

    # we only want download links for the latest version
    versions = []

    for dl in dls:
      versions.append("/".join(dl.split("/")[:-1]))

    versions.sort(reverse=True)
    dls = [ dl for dl in dls if versions[0] in dl ]

    for matching in self.matchAll(dls, link):
      self.downloads.append("https://github.com" + matching)

  def downloadFile(self, url):
    localFile = url.split('/')[-1]
    downFile = requests.get(url, stream=True)

    with open(os.path.join(self.pluginDir, localFile), "wb") as f:
        shutil.copyfileobj(downFile.raw, f)

  def downloadAll(self, progress, task, download = True):
    # first move all the old .jar files from the plugins folder to a safe place
    # i.e. old-plugin-dir
    if download:
      if not os.path.isdir(self.pluginDir):
        progress.console.print("plugin-dir does not exist! please verify plugins.yml!", style="bold red")
        exit()

      oldPluginFiles = glob(os.path.join(self.pluginDir, "*.jar"))

      if os.path.isdir(self.oldPluginDir):
        for oldPluginFile in oldPluginFiles:
          movefrom = oldPluginFile
          moveto = os.path.join(self.oldPluginDir, os.path.split(oldPluginFile)[-1:][0])

          progress.console.print("moving " + movefrom + " to " + moveto + "...", style="italic blue")

          os.rename(movefrom, moveto)
      else:
        progress.console.print("old-plugin-dir does not exist! please verify plugins.yml!", style="bold red")
        exit()

    for downloadURL in self.downloads:
      if download:
        self.downloadFile(downloadURL)
        progress.advance(task)
      else:
        progress.console.print(downloadURL)

@click.command()
@click.option("--config", default="plugins.yml", help="path to plugins.yml or compatible config file")
@click.option("--download/--urls",
              default=True,
              help="automatically download (default behaviour) or only return plugin URLs")
def updatePlugins(config, download):
  with open(config, "r") as stream:
    try:
      data = yaml.safe_load(stream)
      downloader = Downloader(data["config"])

      # find the total number of URLs
      totalURLs = 0

      for key in data["downloads"]:
        for item in data["downloads"][key]:
          totalURLs += 1

      with Progress() as progress:
        urlTask = progress.add_task("[green]Getting plugin URLs...", total=totalURLs)

        for key in data["downloads"]:
          if key == "bukkit":
            for value in data["downloads"][key]:
              progress.console.print(f"Getting URL from {value['url']} ...", style="blue")
              downloader.bukkit(value)
              progress.advance(urlTask)

          if key == "jenkins":
            for value in data["downloads"][key]:
              progress.console.print(f"Getting URL from {value['url']} ...", style="blue")
              downloader.jenkins(value)
              progress.advance(urlTask)

          if key == "github":
            for value in data["downloads"][key]:
              progress.console.print(f"Getting URL from {value['url']} ...", style="blue")
              downloader.github(value)
              progress.advance(urlTask)

        downloadTask = progress.add_task("[green]Downloading plugins...", total=totalURLs)
        downloader.downloadAll(progress, downloadTask, download=download)
        progress.console.print(f"done \o/", style="green bold")

    except yaml.YAMLError as exc:
      print(exc)

if __name__ == "__main__":
  updatePlugins()
