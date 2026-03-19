"""Entry point for running The CISO Council as a module.

Usage: python -m council --scenario scenarios/incident_response/vendor_breach.yaml
"""

from council.cli import main

if __name__ == "__main__":
    main()
