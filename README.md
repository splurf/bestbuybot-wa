# bestbuybot-wa

### This is a Best Buy Bot which automates the add-to-cart/checkout process of any purchase.

# Description
**bestbuybot-wa** uses the popular, yet slow, *Web UI Testing Suite* known as `selenium`.
This bot uses any installed browser specified by the user and attempts to purchase the specified product by SKU.

# Instructions
In order to run this project:
  1.  Clone this repository `git clone https://github.com/splurf/bestbuybot-wa`
  2.  Download the most recent version of [this](https://github.com/mozilla/geckodriver/releases) (should be near the top of the page and look something like this `geckodriver-v0.30.0-win64.zip` if you are on Windows)
  3.  Extract that little guy and place it into this project (the folder which you just cloned)
  
# How to use
This project is command-line dependant, meaning, the information needed for this project to work is all provided through the command line.

You must have a valid Best Buy account with the payment and delivery forms already filled out. Be sure that your payment methods are saved and are valid as well as the delivery address.

The format for calling this script via command line:\
```cmd
python <PATH_TO_INIT> <BROWSER> <SKU> <EMAIL> <PASSWORD> <CVV> [Optional]<TEST>
```

Here's an example of a test run:
```cmd
python ./__init__.py firefox 6429442 johndoe@gmail.com abigai1822 420 test
```

##  Notes
- If you don't want to go into testing mode, then don't include "test" at the end of the command

##  Development
I made this just to see if people would be interested in it. The best bots are written in faster languages and don't use modules like `selenium`. That being said, because this project is completely *Web Automated*, there's potential to many bugs and inconsistencies. Although not perfect, this project seems pretty reliable, but it is slow because it's `selenium` lmao.
