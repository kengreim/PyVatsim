# What is Vatsim Py-API?
Vatsim Py-API is a Python library to interact with data from Vatsim's datafeed, currently located at: http://data.vatsim.net/. It implements Python objects to access the underlying Vatsim data in a Pythonic way, and also parses certain data into developer friendly formats (e.g., timestamp strings into Python datetime objects). 

Because Vatsim's datafeed is updated every ~15 seconds, Py-API supports configurable caching of data from the datafeed so that each access method does not fetch the datafeed (although a "force update" override exists if needed).

# How do I use it?

# Examples
```
vatsim = VatsimAPI()
p = vatsim.pilots()
for cid, pilot in p.items():
    print(cid)
```

# License
Vatsim Py-API is licensed under the MIT License.
