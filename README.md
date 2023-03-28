# NYU DevOps Project - Shopcarts

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a class project for DevOps and Agile Methodologies (CSCI-GA.2820) at New York University, taught by Professor John Rofrano.

## Overview

The shopcarts resource allow customers to make a collection of products that they want to
purchase. It contains a reference to a product id, product name, and the quantity the
customer wants to buy. It also contains the price of the product at the time they placed it in
the cart. A customer will only have one shopcart. Since this is really a collection of product
items, you will need to implement a subordinate REST API to add items to the shopcarts
collection (e.g., /shopcarts/{id}/items). You also will need to associate the shopcart with
a customer preferably through their customer id. A good action for the shopcart API is to be able
to empty or purchase a shopcart.


## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```
## Schema
```SQL
    Shopcart{
        id          Int         PrimaryKey
        customer_id Int 
    }

    Item{
        id          Int         PrimaryKey
        shopcart_id Int         ForeignKey
        product_id  Int
        name        VarChar
        price       Double
        count       Int
    }
```

## Usage
This service has a single page UI available at `/`, and there are also RESTful APIs for integration of the application.
### Get
- List all shopcarts
- Read a shopcart
- List all items in a shopcart
- Read an item in a shopcart
### POST
- Create a shopcart
- Add an item to a shopcart

### DELETE

### PUt

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
