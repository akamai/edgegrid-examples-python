README
===


Description
---

This script will allow you to collect info on Luna Groups, Akamai Contracts, Akamai Products, create CPCodes, manipulate Delivery configs, and activate Delivery configs.


Requirements
---

#### Python3
This script uses python3 (available by [brew.sh](https://brew.sh)), and a couple of python3 libraries. These can be installed on a Mac with:

``` bash
# Install Brew
ladmin$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install Python3 and tools
ladmin$ brew install python3
ladmin$ pip3 install --upgrade pip setuptools wheel
```

#### Python Libraries
These scrips use three python Libraries: `requests`, `edgegrid-python`, and `jsonpatch`.

``` bash
### Use requirements.txt
ladmin$ pip3 install -r requirements.txt

### Or one at a time
ladmin$ pip3 install requests
ladmin$ pip3 install edgegrid-python
ladmin$ pip3 install jsonpatch
```

#### EdgeGridAuth
To use this script you will need API Credentials.  Please follow the directions at: [developer.akamai.com/api/getting-started](https://developer.akamai.com/api/getting-started)

This script assumes by default you have your API credentials saved in a text file located at `~/.edgerc`.  You can use the `--edgerc` to point to a different file, or `--section` to specify the API credentials you would like to use.  You can see an example of this at: [developer.akamai.com/api/getting-started#addcredentialtoedgercfile](https://developer.akamai.com/api/getting-started#addcredentialtoedgercfile) 


AkaPAPI.py Help Menu
---

``` bash
ladmin$ AkaPAPI.py -h
usage: AkaPAPI.py [-h] [--cid CID] [--gid GID] [--pid PID] [--vid VID]
                  [--VERSION {LATEST,STAGING,PRODUCTION}] [--prd PRD]
                  [--cpname CPNAME] [--network {STAGING,PRODUCTION}]
                  [--email EMAIL] [--file FILE] [--edgerc EDGERC]
                  [--section SECTION] [--account-key ACCOUNT_KEY] [-v] [-V]
                  {groups,contracts,products,cpcodes,new-cpcode,properties,property,edge-hostnames,versions,config,new-config,patch,activate}

This script will allow you to collect info on Luna Groups, Akamai Contracts,
Akamai Products, create CPCodes, manipulate Delivery configs, and activate
Delivery configs.

positional arguments:
  {groups,contracts,products,cpcodes,new-cpcode,properties,property,edge-hostnames,versions,config,new-config,patch,activate}
                        Primary "Command": Use the "groups" and "contracts"
                        commands first as they are needed for almost
                        everything when using the PAPI API. You will need to
                        use the "products" command if you are creating a
                        CPCode.

optional arguments:
  -h, --help            show this help message and exit
  --cid CID             Optional flag to identify the Contract ID (beginning
                        with ctr_) when sending commands. (default: None)
  --gid GID             Optional flag to identify the Group ID (beginning with
                        grp_) when sending commands. (default: None)
  --pid PID             Optional flag to identify the Property ID (beginning
                        with prp_) when sending commands. (default: None)
  --vid VID             Optional flag to identify the version number for a
                        specific config. (default: None)
  --VERSION {LATEST,STAGING,PRODUCTION}
                        Optional flag used when creating a new version of a
                        configuration, indicating which version to base the
                        new version from. (default: LATEST)
  --prd PRD             Optional flag that you can use to identify your
                        Product in commands. You need a product identifier to
                        create new edge hostnames, CP codes, or properties.
                        (default: None)
  --cpname CPNAME       Optional flag that you can use to give your CPCode
                        name when creating a CPCODE (default: None)
  --network {STAGING,PRODUCTION}
                        Optional flag specifying which Akamai Network to push
                        the configuration. (default: STAGING)
  --email EMAIL         Optional flag that you can use to identify an email
                        address in commands such as activating a config. You
                        can use multiple times to add additional email
                        addresses. (E.X. --email user1@gov.mil --email
                        user2@gov.mil) (default: None)
  --file FILE           Optional flag that you can use for the "patch"
                        command. At this time the CSV file would be three
                        columns: "hostname", "cpcode", and "edgekey name"
                        (default: False)
  --edgerc EDGERC       Select your ".edgerc" file vs. the default assumption
                        that it is located in your home directory (default:
                        False)
  --section SECTION     If your ".edgerc" has multiple [sections], you can
                        pick which section. (default: default)
  --account-key ACCOUNT_KEY
                        Akamai Employees can switch accounts using their GSS
                        API accountSwitchKey credentials. (default: None)
  -v, --verbose         Optional flag to display extra fields from the Alert
                        API request (default: False)
  -V, --version         Show the version of AkaPAPI.py and exit

Use positional arguments first, then optional ones if needed.


ladmin$ AkaPAPI.py -V
AkaPAPI.py 1.0.0

```