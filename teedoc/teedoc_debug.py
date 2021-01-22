import sys, os

curr_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_path)
from teedoc_main import main

site_path = "examples/teedoc_site"
sys.argv.append("-p")
sys.argv.append(site_path)
sys.argv.append("build")

main()
