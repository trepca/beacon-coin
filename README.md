# Beacon coin

Beacon coin is a Chia singelton coin that can store data that needs to be: 
 - always available
 - censorship resistant
 - versioned
 - potentially immutable

You might want to use it for coordinating peers in a network, storing DNS information or whatever else you think of. (please share though). 
I wrote this mainly to learn more about Chialisp and explore smart coins in Chia Network (especially singletons). 
I used some general principles that could be expanded to implement a smart contract type of coin, with methods and state etc.

This code is still work in progress so *please DO NOT USE it on mainnet*. Use at your own risk. 

**Please note that I'm not affiliated with Chia Network.**

# How to use

You'll need a testnet chia node and wallet with some mojos. Once wallet and node are synced, install the repo.

## For Unix/Macs

Clone this repo in a directory. 

```bash
python3 -m venv venv
. ./venv/bin/activate
pip install beacon
beacon-coin --help
```

It should work on Windows too, but don't really have easy access to it to test. 

## Usage

```bash
Usage: beacon-coin [OPTIONS] COMMAND [ARGS]...

  Manage beacon coins on Chia network.

  They can be used to store key information in a decentralized and durable
  way.

Options:
  --config-path TEXT  Path to your Chia blockchain config (usually ~/.chia).
                      Defaults to fetching it from CHIA_ROOT env var.

  --fingerprint TEXT  Key fingerprint, will default to first one it finds if
                      not provided.

  -v, --verbose       Show more debugging info.
  --help              Show this message and exit.

Commands:
  add-pair      Add a pair of strings to coin data.
  change-owner  Change the owner, works on mutable and immutable coins.
  freeze        Freezing makes the coin immutable
  get-data      Returns a JSON of coin data and metadata Can be piped into...
  mint          Mint a new beacon coin, returns a LAUNCHER_ID.
  remove-pair   Remove a pair at a specifed index from coin data.
```

First you'll need to mint a beacon coin:

```bash
$ beacon-coin mint --fee=10 
Minted a new beacon coin with id: 3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12

Track transaction: 070d0ed91de0ce80c884f13ecad4db02d9d63ae028244e1e55dc69aac1b7904f     Fee: 10 mojos

NOTE: Store launcher_id somewhere safe as this wallet doesn't keep it anywhere yet.
```

Wait until transaction is processed.

You can use `cdv mempool -txid 070d0ed91de0ce80c884f13ecad4db02d9d63ae028244e1e55dc69aac1b7904f`

Let's check contents first:
```bash
$ beacon-coin get-data 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12
{"version": 1, "data": []}
```

Ok, now let's add some data:
```bash
$ beacon-coin add-pair --fee=10 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12 "some" "data"
Added pair ('some', 'data') using transaction: 364eeab9433f6bbf382f2659bdf5bc23c51ae862a765b3d3fdfcf56fe9c8bf1e
```
Wait again for node to process it.

And let's check content again:
```bash
$ beacon-coin get-data 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12                       
{"version": 2, "data": [[0, ["some", "data"]]]}
```
Ok, we just stored some data on Chia blockchain. 

Let's add more and test the removal.

```bash
$ beacon-coin add-pair --fee=10 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12 "more" "data"
Added pair ('more', 'data') using transaction: 4e1ed3b76c474a73d68781d328b130d408bacd6650b4018d63231581655aac33
```

```bash
$ beacon-coin get-data 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12                       
{"version": 3, "data": [[0, ["more", "data"]], [1, ["some", "data"]]]}
```
```bash
$ beacon-coin remove-pair --fee=15 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12 0
Removed pair at 0 using transaction: efbbe9fbeadc78c0840f3bffbda57ea1f8d734cbb634992fcd5e4aa28c4a5ab1
```

```bash
$ beacon-coin get-data 0x3085341ed92faeda6887f5270b7cc049c024bd2bf1c27a9e8f33e1f902fbea12
{"version": 4, "data": [[0, ["some", "data"]]]}
```

# TODOs
- [ ] refactor wallet and make it more DRY 
- [ ] publish tests (right now still in progress)
- [ ] add soft linking between different coins, can enable things like having an immutable beacon coin that points to other mutable coins