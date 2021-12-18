#!/usr/bin/env python3
import asyncio
from functools import wraps
from chia.util.byte_types import hexstr_to_bytes
import json
import click

from beacon.wallet import BeaconWallet

VERBOSE = False


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def debug(msg):
    global VERBOSE
    if VERBOSE:
        click.echo(msg)


def parse_launcher(ctx, param, value):
    try:
        if not value:
            raise ValueError
        if not isinstance(value, (str, bytes)):
            raise ValueError
        if len(value) != 66:
            raise click.BadArgumentUsage(
                "Launcher ID must start with 0x and be 66 chars long"
            )
        if value[:2] != "0x":
            raise click.BadArgumentUsage("Launcher ID must start with 0x")
        return hexstr_to_bytes(value)
    except click.BadArgumentUsage:
        raise
    except Exception as e:
        raise click.BadArgumentUsage("Not a valid launcher ID")


@click.group()
@click.option("--config-path", default=None)
@click.option("--fingerprint", default=None)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx, config_path, fingerprint, verbose):
    if verbose:
        global VERBOSE
        VERBOSE = True
    debug(f"Connecting to wallet...")
    wallet = BeaconWallet.create(fingerprint, config_path, verbose=verbose)
    ctx.obj = wallet


@click.command(help="Mint a new beacon coin, returns a LAUNCHER_ID.")
@click.option(
    "--fee",
    type=int,
    default=0,
    help="Transaction fee, defaults to 0",
)
@coro
@click.pass_context
async def mint(ctx, fee):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug("Minting a new coin for wallet: %s" % wallet.wallet_address)
        tx_id, launcher_id = await wallet.mint(fee=fee)
        debug("Got back tx_id: %s, launcher_id: %s" % (tx_id, launcher_id))
        if tx_id and launcher_id:
            click.echo(
                f"Minted a new beacon coin with id: {launcher_id}\n\n"
                f"Track transaction: {tx_id}"
                f"\tFee: {fee} mojos"
                "\n\nNOTE: Store launcher_id somewhere safe as this wallet doesn't keep it anywhere yet.\n"
            )
        else:
            click.echo("Failed to mint for unknown reason.")


@click.command(name="add-pair")
@click.option(
    "--fee",
    type=int,
    default=0,
    help="Transaction fee, defaults to 0",
)
@click.argument("launcher-id", callback=parse_launcher)
@click.argument("key", type=str)
@click.argument("value", type=str)
@coro
@click.pass_context
async def add_pair(ctx, launcher_id, key, value, fee):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug(
            f"Adding pair ({repr(key)}, {repr(value)}) to beacon coin: {launcher_id.hex()}"
        )
        tx_id = await wallet.add_pair(launcher_id, (key, value), fee=fee)
        click.echo(f"Added pair ('{key}', '{value}') using transaction: {tx_id}")


@click.command(name="remove-pair")
@click.option(
    "--fee",
    type=int,
    default=0,
    help="Transaction fee, defaults to 0",
)
@click.argument("launcher-id", callback=parse_launcher)
@click.argument("index", type=int)
@coro
@click.pass_context
async def remove_pair_at(ctx, launcher_id, index: int, fee: int):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug(f"Removing pair at index {index} from beacon coin: {launcher_id}")
        tx_id = await wallet.remove_pair_at(launcher_id, index, fee)
        click.echo(f"Removed pair at {index} using transaction: {tx_id}")


@click.command(name="freeze")
@click.option(
    "--fee",
    type=int,
    default=0,
    help="Transaction fee, defaults to 0",
)
@click.argument("launcher-id", callback=parse_launcher)
@coro
@click.pass_context
async def freeze(ctx, launcher_id, fee):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug(f"Freezing beacon coin: {launcher_id}")
        tx_id = await wallet.freeze(launcher_id, fee=fee)
        click.echo(f"Beacon coin frozen using transaction: {tx_id}")


@click.command(name="change-owner")
@click.option(
    "--fee",
    type=int,
    default=0,
    help="Transaction fee, defaults to 0",
)
@click.argument("launcher-id", callback=parse_launcher)
@click.argument("new-pub-key")
@coro
@click.pass_context
async def change_owner(ctx, launcher_id, new_pub_key, fee):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug(f"Changing ownership to {new_pub_key} on beacon coin: {launcher_id}")
        tx_id = await wallet.set_ownership(launcher_id, new_pub_key, fee=fee)
        click.echo(f"Ownership changed to {new_pub_key} using transaction: {tx_id}")


@click.command(name="get-data")
@click.argument("launcher-id", callback=parse_launcher)
@coro
@click.pass_context
async def get_data(ctx, launcher_id):
    wallet: BeaconWallet
    async with ctx.obj as wallet:
        debug(f"Fetching data for beacon coin: {launcher_id.hex()}")
        data = await wallet.get_data(launcher_id)
        debug(f"Got back data: {data}")
        pretty_data = {
            "version": data[0],
            "data": [(i, x) for i, x in enumerate(data[1])],
        }

        class BytesDump(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, bytes):
                    return obj.decode()
                return json.JSONEncoder.default(self, obj)

        click.echo(json.dumps(pretty_data, cls=BytesDump))


cli.add_command(mint)
cli.add_command(add_pair)
cli.add_command(remove_pair_at)
cli.add_command(change_owner)
cli.add_command(get_data)
cli.add_command(freeze)

if __name__ == "__main__":
    cli()
