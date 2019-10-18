from eth_account import Account


class Wallet(object):
    @staticmethod
    def new(key):
        try:
            new_account = Account.create('voting' + key)

            with open("address".format(key), "w") as f:
                f.write(str(new_account.address))

            with open("private_key".format(key), "w") as f:
                f.write(str(new_account.privateKey))

            return True
        except Exception as e:
            print(e)
            return False


key = str(input("wallet key : "))
if Wallet.new(key=key):
    print("Make new wallet successfully.")
else:
    print("===[ Error ]===")
