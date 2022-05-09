from logging import Logger
import click

logger = Logger(__file__)


@click.command()
@click.argument('RAW_DATA_DIR', help='should contain meta.csv, eeg.csv, and info.csv in this directory')
@click.argument('OUTPUT_PATH')
@click.option('--train', help='proportion for training set')
@click.option('--val', help='proportion for validation set')
@click.option('--test', help='proportion for testing set')
def main(RAW_DATA_DIR, OUTPUT_PATH, train, val, test):
    assert train + val + test == 1


if __name__ == '__main__':
    main()
