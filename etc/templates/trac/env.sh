#!/bin/bash
# Root path to multiproject setup
ROOT="${trac_root}"

# -- Following variables are only used by deploy.sh

# Deploy setting, if anything else than production, no activation is performed
ENVIRONMENT="production"

# Should batchmodify trac plugin be installed
BATCHMODIFY=1

# Should childtickets trac plugin be installed
CHILDTICKETS=1