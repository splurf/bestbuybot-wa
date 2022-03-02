from util.bot import Bot


def main():
    bot = Bot.from_args()

    if not bot:
        return print("Invalid arguments")

    if not bot.get_product_url():
        return bot.shutdown("Invalid SKU")

    if not bot.update_product():
        return bot.shutdown("Failed to update product")

    print("\nSKU: %s\nModel: %s\nName: %s\n" %
          (bot.product.sku, bot.product.model, bot.product.name))

    if not bot.login("Logging in"):
        return bot.shutdown("Failed to login")

    bot.wait_until_in_stock()

    if not bot.add_to_cart("Adding to cart"):
        return bot.shutdown("Failed to add to cart")

    if not bot.cart("Going to cart"):
        return bot.shutdown("Failed to go to cart")

    if not bot.checkout("Checking out"):
        return bot.shutdown("Failed to continue to check out item")

    bot.continue_optional("Continuing to payment if necessary")

    bot.enter_cvv("Entering CVV if necessary")

    if bot.test():
        input("Test Run Successfully Completed")
        bot.shutdown(block=False)
    else:
        msg: str
        if bot.place_order("Placing order"):
            if bot.evaluate():
                msg = "Successfully Purchased"
            else:
                msg = "Failed to Purchase"
        else:
            msg = "Failed to place order"
        bot.shutdown(msg)


if __name__ == "__main__":
    main()
