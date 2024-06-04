#!/usr/bin/env python3

import json
import argparse
import urllib.request as urllib
import pandas as pd

import matplotlib.pyplot as plt

ARCHIVER_INFIX="/retrieval/data/getData.json?pv="

def get_args():
    """
    Allows getting PV as command-line argument
    """
    RED = '\033[91m'
    RESET = '\033[0m'
    desc = (f'{RED}WARNING: {RESET}archiver provides PV timestamp in the "secs" column. This is in UTC time, java epoch. You will have to convert it to your UTC.')
    
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-p", "--pv", 
                        type=str,
                        required=True,
                        help="PV name to search.")
    parser.add_argument("-f", "--print",
                        type=bool,
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help="Print recovered data.")
    parser.add_argument("-b", "--begin",
                        type=str,
                        help="Starting time to get values. \
                        Formatted as YYYY-MM-DD-HH-mm-ss-(ms)(ms)(ms). \
                        Example: 2024-06-03-14-01-01-565.")
    parser.add_argument("-e", "--end",
                        type=str,
                        help="Ending time to get values. \
                        Formatted as YYYY-MM-DD-HH-mm-ss-(ms)(ms)(ms). \
                        Example: 2024-06-03-14-01-01-565.")
    parser.add_argument("-a", "--archiver",
                        type=str,
                        required=True,
                        help="Archiver url preffix. Example: https://myarchiver.com")
    parser.add_argument("--plot",
                        type=bool,
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help="Plot results (only VALxTimestamp)")
    
    args = parser.parse_args()
    return args

class PVGetter:

    def __init__(self, archiver, PV, begin = None, end = None):
        """
        Class to store pv data retrieved from archiver as a pandas DataFrame.
        """

        self.archiver = archiver
        self.pv = PV
        self.begin = begin
        self.end = end
        self.df = None
        self.json = None
        self.url = None
        
        self.get_url()

    def get_url(self):
        """
        Assemble url to make request based on arguments.

        Uses:
            self.archiver
            self.pv
            self.begin
            self.end

        Modifies:
            self.url
        """

        pv_for_url = self.pv.replace(":","%") #PV formatting
        begin_suffix = ""
        end_suffix = ""
        
        if self.begin is not None:
            b = self.begin.split("-")
            begin_suffix += "&from={}-{}-{}T{}%3A{}%3A{}Z".format(b[0], b[1], b[2],
                                                            b[3], b[4], b[5]) 
            
        if self.end is not None:
            e = self.end.split("-")
            end_suffix += "&to={}-{}-{}T{}%3A{}%3A{}Z".format(e[0], e[1], e[2],
                                                            e[3], e[4], e[5])

        self.url = "{}{}{}{}".format(self.archiver, ARCHIVER_INFIX, pv_for_url, begin_suffix, end_suffix)
        
    def getPV(self):
        """
        Gets set of values in given period and stores as json and DataFrame.
        
        Uses:
            self.url
            
        Modifies:
            self.df
            self.json
        """
        req = urllib.urlopen(self.url)
        self.json = json.load(req)[0]["data"]
        self.df = pd.DataFrame(self.json)
        
        self.convert_epoch()
            
    def convert_epoch(self):
        """
        From DataFrame, convert 'secs' column into
        timestamp.
        
        Uses:
            self.df
            
        Modifies:
            self.df
        """
        self.df["timestamps"] = pd.to_datetime(self.df["secs"], unit="s")
        
    def plot(self, *args, **kwargs):
        """
        Plot self.dataframe with defined args.
        Plotting interface is exactely equal to pandas plot interface, so
        arguments should be identical. 
        """
        self.df.plot.scatter(x="timestamps", y="val")

def main():

    args = get_args()
    
    getter = PVGetter(args.archiver, args.pv, args.begin, args.end)
    getter.getPV()
    
    if args.print:
        print(getter.df)
        
    if args.plot:
        getter.plot()
        plt.show()

if __name__== "__main__":
    main()