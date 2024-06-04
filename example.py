#!/usr/bin/env python3

from get import PVGetter

getter = PVGetter(archiver="archiver_hostname",
                  PV="PVNAME",
                  begin="2024-06-02-00-00-00-000",
                  end="2024-06-02-00-00-10-000")
getter.getPV()

print(getter.df)