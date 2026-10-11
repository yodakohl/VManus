"""Replay the locked primary, then the explicitly post-result explanation."""
import sys
sys.dont_write_bytecode = True
import run
import explain_nq
if __name__ == '__main__':
    run.main()
    explain_nq.main()
