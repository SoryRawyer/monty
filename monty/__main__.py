"""
__main__.py : run the monty gui
"""

from monty.app import main

if __name__ == '__main__':
    try:
        main().main_loop()
    except Exception as err:
        print(err)
        raise err
