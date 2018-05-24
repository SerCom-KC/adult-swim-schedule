#!/bin/bash

echo Cloning repository
git clone https://${GH_TOKEN}@github.com/$TRAVIS_REPO_SLUG master
echo -e \\033[32mRepository cloned successfully\\033[0m
