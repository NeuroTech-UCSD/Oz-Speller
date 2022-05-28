import pickle
import matplotlib
import click


@click
@click.argument(input_path)
@click.argument(output_path)
def main(input_path, output_path):
    
with open