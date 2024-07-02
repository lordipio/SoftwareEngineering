
import pandas as pd


class Person:
    def __init__(self, userName, password, age, wallet, address) -> None:

        self.userName = userName

        self.password = password

        self.age = age

        self.wallet = wallet

        self.address = address


    def UpdateWallet(self, fileName):

        print('Enter wallet number: ')

        command = int(input())

        self.wallet += command

        df = pd.read_excel(fileName)

        df.loc[df['UserName'] == self.userName, 'Wallet'] = self.wallet

        # Save the updated DataFrame back to the Excel file
        df.to_excel(fileName, index=False)

        print ('Your new wallet number is: ', self.wallet)



    def UpdateAddress(self, fileName):

        print('Enter the new address: ')
        
        command = str(input()).lower()

        new_address = command

        if not new_address:
            print("Address should not be empty!")
            return
    
        parts = new_address.split(",")
        print(len(parts))
        if len(parts) != 4:
            print("Address should be in (city, street, alley, house number) format")
            return
    
        if not parts[0].strip():
            print("city should not be empty!")
            return
    
        if not parts[3].strip():
            print("house number should not be empty")
            return

        self.address = new_address

        df = pd.read_excel(fileName)

        df.loc[df['UserName'] == self.userName, 'Address'] = new_address

        # Save the updated DataFrame back to the Excel file
        df.to_excel(fileName, index=False)

        print(self.address)



userCanEnter = False


while True:

    print ('Sign Up or Login?')

    command = str(input())

    command = command.lower()
    
    if command == 'login':
        print('Enter User Name: ')
        userName = str(input())

        print('Enter Password: ')
        password = str(input())

        usersInfo = pd.read_excel('UsersInfo.xlsx')

        # Check if the username exists
        if userName not in usersInfo['UserName'].values:
            print("Username does not exist.")
            break
    
        # Check if the username and password match
        user_data = usersInfo[usersInfo['UserName'] == userName]
        if user_data['Password'].values[0] == password:
            print("Welcome ", userName)
            userCanEnter = True
            person = Person(userName, password, user_data['Age'].values[0], user_data['Wallet'].values[0], user_data['Address'].values[0])


        else:
            print("Username and password do not match.")
            print('\n \n')


        while userCanEnter:


            print('Do you want to charge your wallet? (yes/no)')

            command = str(input()).lower()

            if command == 'yes':
                person.UpdateWallet('UsersInfo.xlsx')


            print('You can change your address by typing (Change Address). Type something else to continue.')

            command = str(input()).lower()

            if command == 'change address':
                person.UpdateAddress('UsersInfo.xlsx')

                person.address





    if command == 'sign up':
        print('Enter User Name: ')
        userName = str(input())

        print('Enter Password: ')
        password = str(input())

        print('Enter Age: ')
        age = int(input())
        
        print('Enter Wallet: ')
        wallet = int(input())

        print('Enter Address: ')
        address = str(input())

        
        newUserData = {
        'UserName': userName,
        'Password': password,
        'Age': age,
        'Wallet': 0,
        'Address': address
        }

        newUserData = pd.DataFrame([newUserData])

        usersInfo = pd.read_excel('UsersInfo.xlsx')

        usersInfo = pd.concat([usersInfo, newUserData], ignore_index=True)
        
        usersInfo.to_excel('UsersInfo.xlsx', index=False)
        
        user = Person(userName, password, age, wallet, address)










