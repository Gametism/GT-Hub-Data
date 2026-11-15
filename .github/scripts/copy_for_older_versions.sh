#!/bin/bash
# Writes sidewarden-data.txt: the list as gt-hub-data.txt has it, for the versions that read it under its
# old name (Sidewarden 0.11.0 to 0.11.22, GT-Hub 0.11.23). The same lines, with a note on top that says
# where to edit; the versions skip lines that start with ";".
set -e
cd "$(dirname "$0")/../.."
{
    printf '; A copy of gt-hub-data.txt, made by itself whenever that file changes - edit gt-hub-data.txt, not this one.\n'
    printf '; It is here for the versions that read the list under its old name: Sidewarden 0.11.0 to 0.11.22, GT-Hub 0.11.23.\n'
    cat gt-hub-data.txt
} > sidewarden-data.txt
