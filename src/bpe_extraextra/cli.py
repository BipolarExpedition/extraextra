#!/usr/bin/env python

# Project: extraextra
# Package: bpe_extraextra
# Description: Program for reading a config file and applying updates to installed servers. Primarily modded Minecraft servers.
# Author: BipolarExpedition(Doc1979)
# Email: lastdoc39@gmail.com
# License: MIT
# Repository (if exists): "https://github.com/BipolarExpedition/extraextra"

"""
A CLI interface for extraextra.

File is bpe_extraextra.cli.py
"""

import argparse
import logging
#import sys

# Configure logging
def setup_logging(log_level=logging.INFO):
    """
    Set up logger interface. log_level defaults to INFO
    """

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def setup_argument_parser():
    """
    Set up argument parser
    """

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="A CLI interface for extraextra")
    
    # Add optional arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Increase output verbosity"
    )
    
    parser.add_argument(
        '--log',
        type=str,
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        'action',
        type=str,
        choices=['start', 'stop', 'status'],
        help="Action to perform"
    )
    
    # Parse args, and return the object
    return parser.parse_args()


# Main function for CLI handling
def main():
    """
    Main function for CLI handling
    """
    
    args = setup_argument_parser()

    # Set up logging based on user input
    log_level = getattr(logging, args.log.upper(), logging.INFO)
    setup_logging(log_level)

    if args.verbose:
        print("Running with verbose output...")

    # CLI logic based on the chosen action
    if args.action == 'start':
        logging.info("Starting the tool...")
        # Add your start logic here
    elif args.action == 'stop':
        logging.info("Stopping the tool...")
        # Add your stop logic here
    elif args.action == 'status':
        logging.info("Checking status...")
        # Add your status logic here

if __name__ == "__main__":
    main()
