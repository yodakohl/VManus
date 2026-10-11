"""Run the independent main validator and explanatory-certificate checker."""
import sys
sys.dont_write_bytecode = True
import validate
import validate_cores
if __name__ == '__main__':
    validate.main()
    validate_cores.main()
