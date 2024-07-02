
# Importing ----------------------------------------------------------------
import pandas as pd

import os
#  -------------------------------------------------------------------------  

# Exception ----------------------------------------------------------------
class CustomError(Exception):

    def __init__(self, message):

        self.message = message

        super().__init__(self.message)

#  -------------------------------------------------------------------------        

# Read Products From Give File ---------------------------------------------
def read_product_csv(file_name : str) -> list:

    try:
        csv_file_info = pd.read_csv(file_name)
        products = []
        product = None

        for index, row in csv_file_info.iterrows():
            product = Product(row['ID'], row['Name'], row['Type'], row['Price'], row['Is_available'], row['Rate'])
            products.append(product)

        return products

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

#  -------------------------------------------------------------------------

# Create Product Class -----------------------------------------------------
class Product:
    def __init__(self, product_id = 0, product_name = '', product_type = '', product_price = 0, product_availability = False, product_rate = 0):
        
        self.product_id = product_id
        
        self.product_name = product_name
        
        self.product_type = product_type
        
        self.product_price = product_price
        
        self.product_availability = product_availability
        
        self.product_rate = product_rate

#  -------------------------------------------------------------------------

# Create Shopping Cart Class -----------------------------------------------
class ShoppingCart():
    
    def __init__(self, products_id) -> None:
        self.products_id = products_id

# ////////////////////////////////////////////////////////

    def add_product(self, product_id : Product) -> None:
        self.products_id.append(product_id)

#  -------------------------------------------------------------------------

# Create User Class --------------------------------------------------------
class User:
    def __init__(self, user_name : str, user_password : str, wallet_balance : float, shopping_cart : ShoppingCart):
        self.file_name = 'UsersData.csv'
        self.wallet_balance = wallet_balance
        self.user_name = user_name
        self.user_password = user_password
        self.shopping_cart = shopping_cart
        self.shopping_cart.products_id = [item for item in self.shopping_cart.products_id if item != 'nan']
        self.remove_unavailable_products_from_cart()

# ////////////////////////////////////////////////////////

    def remove_unavailable_products_from_cart(self):

        product_id_to_be_remove = []

        for product_id in self.shopping_cart.products_id:
            product = self.find_product(product_id)
            
            if not product:
                product_id_to_be_remove.append(product_id)

        for product_id in product_id_to_be_remove:
            self.shopping_cart.products_id.remove(product_id)

        self.__update_users_data_csv()

# ////////////////////////////////////////////////////////

    def charge_wallet(self, charge_amount : int):
        self.wallet_balance += charge_amount
        self.__update_users_data_csv()

# ////////////////////////////////////////////////////////

    def add_product_to_cart(self, product_id) -> None:
        for cart_id in self.shopping_cart.products_id:
            if cart_id == str(product_id):
                return

        self.shopping_cart.add_product(str(product_id))
        self.__update_users_data_csv()

# ////////////////////////////////////////////////////////

    def proceed_cart(self) -> bool:

        global products
        proceeded_cart = False
        cart_products = []
        cart_total_price = 0
        self.shopping_cart.products_id = [item for item in self.shopping_cart.products_id if item != 'nan']

        if len(self.shopping_cart.products_id) == 0:
            self.display_shopping_cart()
            
        for product_id in self.shopping_cart.products_id:
            founded_product = self.find_product(product_id)
            
            if founded_product:
                cart_total_price += founded_product.product_price
                cart_products.append(founded_product)


        if self.wallet_balance >= cart_total_price: # Payment condition is okay
            self.wallet_balance -= cart_total_price
            print('Payment was successful!\n')
            self.display_receipt()

            try:
                df = pd.read_csv('products.csv')

                for product in products: # set product unavailable
                    if product in cart_products:
                        product.product_availability = False

                        if product.product_id in df['ID'].values:
                            # Update the Is_available column for the specified product ID
                            df.loc[df['ID'] == product.product_id, 'Is_available'] = 'FALSE'

                df.to_csv('products.csv', index=False)

            except FileNotFoundError:
                print(f"Error: The file 'product.csv' was not found.")

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            self.shopping_cart.products_id = []
            self.__update_users_data_csv()

            return True

        else:
            print('Not enough money!')

        return proceeded_cart

# ////////////////////////////////////////////////////////

    def display_receipt(self):
        print('------------ Ordered items ------------\n')
        self.display_shopping_cart()

# ////////////////////////////////////////////////////////

    def display_shopping_cart(self):
        cart_products_id = self.shopping_cart.products_id

        if len(cart_products_id) == 0:
            print('The shopping cart is empty!\n\n')
            return

        for product_id in self.shopping_cart.products_id: 
            product = self.find_product(product_id)

            if not product:
                continue

            product_dict = {
            "Name": str(product.product_name),
            "Type": str(product.product_type),
            "Price": str(product.product_price),
            "Rate": str(product.product_rate),
            "Availability": str(product.product_availability)
            }

            max_key_length = max(len(key) for key in product_dict.keys())
            max_value_length = max(len(value) for value in product_dict.values())
            border = "+-" + "-"*max_key_length + "-+-" + "-"*max_value_length + "-+"
            print(border)

            for key, value in product_dict.items():
                print(f"| {key.ljust(max_key_length)} | {str(value).ljust(max_value_length)} |")
                print(border)

            print('\n\n')

# ////////////////////////////////////////////////////////

    def __update_users_data_csv(self) -> None :

        df = pd.read_csv(self.file_name)
        self.shopping_cart.products_id = [item for item in self.shopping_cart.products_id if item != 'nan']

        if self.user_name in df['user_name'].values:
            df.loc[df['user_name'] == self.user_name, 'wallet_balance'] = self.wallet_balance
            df.loc[df['user_name'] == self.user_name, 'shopping_cart_products_id'] = ','.join(map(str, self.shopping_cart.products_id))
            df.to_csv(self.file_name, index=False)

# ////////////////////////////////////////////////////////

    def find_product(self, product_id : int) -> Product:
        global products

        try:
            product_id = int(float(product_id)) # it may raise value error (it should be first float then cast it to int)
            founded_product = None

            for product in products:
                if product.product_id == product_id:
                    founded_product = product

            if founded_product == None:
                raise CustomError('\nNo product found!')


            if founded_product.product_availability == False:
                raise CustomError(f'\nThe product ({founded_product.product_name}) is not available at the moment!') 
        
        except ValueError:
            print('Only enter numbers!')
            return

        except CustomError as e:
            print(e.message)
            return


        else:
            return founded_product

# ////////////////////////////////////////////////////////

    def remove_product(self, product_id) -> bool:
        if product_id not in self.shopping_cart.products_id:
            print('The product is not in your shopping cart!\n')
            return False

        self.shopping_cart.products_id.remove(product_id)
        self.__update_users_data_csv()
        print('The product removed successfully!\n')
        return True

#  -------------------------------------------------------------------------

# Create System Class ------------------------------------------------------
class System:

    def __init__(self) -> None:
        global products
        self.users = []
        self.products = products
        logged_in_user = None
        self.file_name = 'UsersData.csv'

        if not os.path.isfile(self.file_name):
            df = self.__create_users_data_csv()

        else:
            df = pd.read_csv(self.file_name)

        self.__extract_users_from_data_frame(df)

# ////////////////////////////////////////////////////////

    def __create_users_data_csv(self) -> pd.DataFrame:
        columns = ['user_name', 'user_password', 'wallet_balance', 'shopping_cart_products_id']
        df = pd.DataFrame(columns=columns)
        df.to_csv(self.file_name, index=False)

        return df

# ////////////////////////////////////////////////////////

    def __extract_users_from_data_frame(self, df : pd.DataFrame) -> None:

        for _, row in df.iterrows():
            user_name = row['user_name']
            user_password = row['user_password']
            wallet_balance = row['wallet_balance']
            shopping_cart_products_id = str(row['shopping_cart_products_id']).split(',')
            shopping_cart = ShoppingCart(shopping_cart_products_id)
            user = User(user_name, user_password, wallet_balance, shopping_cart)
            self.users.append(user)

# ////////////////////////////////////////////////////////

    def run_system(self) -> None:
        exit_from_system = False

        while exit_from_system == False:
            print('----------------------------')
            print('   | Menu | \n\n--- 1 to LOGIN \n--- 2 to SIGN UP \n--- 3 to EXIT')
            print('----------------------------\n')
            user_command = input('>> ')

            if not self.__menu_command_error_checker(user_command, 1, 3):
                continue

            if int(user_command) == 1:
                self.login_menu()
                self.logged_in_menu()

            if int(user_command) == 2:
                self.sign_up()

            if int(user_command) == 3:
                exit_from_system = True
                break

# ////////////////////////////////////////////////////////

    def sign_up(self):
        while True:
            user_name = input('Enter user name: ')

            if self.check_user_name_availability(user_name) == True:    
                print('\nUser name is already availabe. Try something else.')
                continue

            user_password = input('Enter password: ')
            self.add_new_user(user_name, user_password)
            break

# ////////////////////////////////////////////////////////

    def login_menu(self) -> User:
        while True:
            user_name = input('Enter user name: ')

            if self.check_user_name_availability(user_name) == False:
                print(f"\nThere is no user called '{user_name}'. Try Again! \n\n")
                continue

            user_password = input('Enter password: ')
            user = self.does_user_name_password_match(user_name, user_password)

            if user == None:
                print('\nWrong password. Try again.\n\n')
                continue
            
            else:
                self.logged_in_user = user
                self.logged_in_user.remove_unavailable_products_from_cart()
                break

# ////////////////////////////////////////////////////////

    def logged_in_menu(self):
        
        while True:
            print('\n\n\n----------------------------')
            print('       | Menu | \n\n--- 1 to SEARCH FOR PRODUCT \n--- 2 to PROCEED YOUR SHOPPING CART \n--- 3 to CHARGE YOUR WALLET \n--- 4 to DISPLAY SHOPPING CART \n--- 5 to REMOVE PRODUCT FROM THE SHOPPING LIST \n--- 6 to SHOW YOUR WALLET BALANCE \n--- 7 to LOGOUT')
            print('----------------------------\n')
            user_command = input('>> ')
            
            if not self.__menu_command_error_checker(user_command, 1, 7):
                continue

            # SEARCH FOR PRODUCT
            if int(user_command) == 1:
                product_id = input('Enter product id: ')
                founded_product = self.logged_in_user.find_product(product_id)

                if founded_product == None:
                    continue

                else: 
                    self.product_menu(founded_product)

            # PROCEED SHOPPING LIST
            if int(user_command) == 2:
                self.logged_in_user.proceed_cart()
                continue


            # CHARGE THE WALLET
            if int(user_command) == 3:
                charging_value = input('Enter the charging value: \n')
                
                try:
                    charging_value = float(charging_value)

                    if charging_value < 0: 
                        raise CustomError('\nThen number should be positive!\n\n')

                    self.logged_in_user.charge_wallet(float(charging_value))


                except ValueError:
                    print('\nThe number should be float!\n\n')

                except CustomError as e:
                    print(e.message)

            # DISPLAY SHOPPING CART
            if int(user_command) == 4:
                self.logged_in_user.display_shopping_cart()

            # REMOVE PRODUCT FROM SHOPPING CART
            if int(user_command) == 5:
                removed_product_id = input('Enter product id: \n')
                self.logged_in_user.remove_product(removed_product_id)

            if int(user_command) == 6:
                print(f"{self.logged_in_user.wallet_balance:.2f}", '\n\n')
                continue

            # LOGOUT
            if int(user_command) == 7:
                break


# ////////////////////////////////////////////////////////
    def product_menu(self, founded_product : Product):

        print('\n------------ Product ------------')

        product = {
            "Name": str(founded_product.product_name),
            "Type": str(founded_product.product_type),
            "Price": str(founded_product.product_price),
            "Rate": str(founded_product.product_rate),
            "Availability": str(founded_product.product_availability)
        }

        max_key_length = max(len(key) for key in product.keys())
        max_value_length = max(len(value) for value in product.values())
        border = "+-" + "-"*max_key_length + "-+-" + "-"*max_value_length + "-+"
        print(border)

        for key, value in product.items():
            print(f"| {key.ljust(max_key_length)} | {str(value).ljust(max_value_length)} |")
            print(border)

        while True:
            print('\n \n----------------------------\n')
            print('         | Menu | \n\n--- 1 to ADD PRODUCT TO SHOPPING CART\n--- 2 to GET BACK TO MENU')
            print('----------------------------\n')
            user_command = input('>> ')
            
            if not self.__menu_command_error_checker(user_command, 1, 2):
                continue

            if int(user_command) == 1:
                self.logged_in_user.add_product_to_cart(founded_product.product_id)
                print('added successfully')
                break
                
            if int(user_command) == 2:
                break

# ////////////////////////////////////////////////////////

    def __menu_command_error_checker(self, command : str, min_range : int, max_range : int) -> int:
        try:
            command = int(command)

            if not (min_range <= command <= max_range):
                raise CustomError('\nCommand is not valid. Try again! \n\n\n\n')

            return command

        except ValueError:
            print('\nCommand should be number. Try again! \n\n\n\n')
            return None

        except CustomError as e:
            print(e.message)
            return None

# ////////////////////////////////////////////////////////

    def check_user_name_availability(self, user_name : str) -> bool:
        user_name_founded = False

        for user in self.users:
            if user.user_name == user_name:
                user_name_founded = True

        return user_name_founded

# ////////////////////////////////////////////////////////

    def does_user_name_password_match(self, user_name : str, user_password : str) -> User:
        matched_user = None

        for user in self.users:
            if user.user_name == user_name and user.user_password == user_password:
                matched_user = user

        return matched_user

# ////////////////////////////////////////////////////////
    
    def add_new_user(self, user_name : str, user_password : str) -> None:
        user = User(user_name, user_password, 0, ShoppingCart([]))
        self.users.append(user)

        new_user_data = {
        'user_name': user.user_name,
        'user_password': user.user_password,
        'wallet_balance': user.wallet_balance,
        'shopping_cart_products_id': ','.join([str(product_id) for product_id in user.shopping_cart.products_id])
        }
    
        new_user_df = pd.DataFrame([new_user_data])
        new_user_df.to_csv(self.file_name, mode='a', header=False, index=False)
        print(f"Added new user '{user.user_name}' to '{self.file_name}'")

#  -------------------------------------------------------------------------

# Calling Main Functions For Using In Terminal (if you don't want to use UI, uncomment below lines)---------------------------------------------------

# products = read_product_csv('products.csv')

# system = System()

# system.run_system()




######################################################    UI Code    #######################################################################




# Importing ----------------------------------------------------------------
import tkinter as tk

from tkinter import messagebox

#  -------------------------------------------------------------------------  
# Global Variable
products = read_product_csv('products.csv')

# OnlineShopUI Class -------------------------------------------------------
class OnlineShopUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Shop")
        self.system = System()
        self.login_screen()

# ////////////////////////////////////////////////////////

    def login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Login", font=("Helvetica", 16)).pack(pady=10)  # Add title
        tk.Label(self.root, text="User Name").pack()

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack()

        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.pack()

        tk.Button(self.root, text="Enter", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Sign Up", command=self.sign_up_screen).pack()

# ////////////////////////////////////////////////////////

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.system.does_user_name_password_match(username, password)

        if user:
            self.system.logged_in_user = user
            self.logged_in_menu()
            self.system.logged_in_user.remove_unavailable_products_from_cart()

        else:
            messagebox.showerror("Error", "Invalid username or password")

# ////////////////////////////////////////////////////////

    def sign_up_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Sign Up", font=("Helvetica", 16)).pack(pady=10)  # Add title

        tk.Label(self.root, text="User Name").pack()
        self.signup_username_entry = tk.Entry(self.root)
        self.signup_username_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.signup_password_entry = tk.Entry(self.root, show='*')
        self.signup_password_entry.pack()

        tk.Button(self.root, text="Sign Up", command=self.sign_up).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.login_screen).pack()

# ////////////////////////////////////////////////////////

    def sign_up(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()

        if self.system.check_user_name_availability(username):
            messagebox.showerror("Error", "Username already exists")
        else:
            self.system.add_new_user(username, password)
            messagebox.showinfo("Success", "User signed up successfully")
            self.login_screen()

# ////////////////////////////////////////////////////////

    def logged_in_menu(self):
        self.clear_screen()

        menu_frame = tk.Frame(self.root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
        menu_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(menu_frame, text="Welcome to the Online Shop", font=("Helvetica", 18, "bold"), bg="#F0F0F0").pack(pady=10)

        button_style = {"font": ("Helvetica", 14), "bg": "#4CAF50", "fg": "#FFFFFF", "relief": tk.RAISED, "bd": 2, "padx": 10, "pady": 5}

        tk.Button(menu_frame, text="Search Product", command=self.search_product_screen, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Proceed Cart", command=self.proceed_cart, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Charge Wallet", command=self.charge_wallet_screen, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Display Shopping Cart", command=self.display_cart, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Remove Product from Cart", command=self.remove_product_screen, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Show Wallet Balance", command=self.show_wallet_balance_screen, **button_style).pack(pady=5)
        tk.Button(menu_frame, text="Logout", command=self.logout, **button_style).pack(pady=5)

# ////////////////////////////////////////////////////////

    def search_product_screen(self):
        self.clear_screen()

        # Resize the window to make it bigger
        self.root.geometry("950x600")

        # Create a frame for the search product screen
        search_frame = tk.Frame(self.root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
        search_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(search_frame, text="Search Product", font=("Helvetica", 16)).pack(pady=10)

        tk.Label(search_frame, text="Product ID", font=("Helvetica", 14), bg="#F0F0F0").pack(pady=5)
        self.product_id_entry = tk.Entry(search_frame, font=("Helvetica", 14), bd=2, relief=tk.SUNKEN)
        self.product_id_entry.pack(pady=5)

        button_style = {"font": ("Helvetica", 14), "bg": "#4CAF50", "fg": "#FFFFFF", "relief": tk.RAISED, "bd": 2, "padx": 10, "pady": 5}

        tk.Button(search_frame, text="Search", command=self.search_product, **button_style).pack(pady=10)
    
        # Add a scrollable frame to display all available products
        available_products_frame = tk.Frame(search_frame, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
        available_products_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
        canvas = tk.Canvas(available_products_frame, bg="#F0F0F0")
        scrollbar = tk.Scrollbar(available_products_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F0F0F0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for product in self.system.products:
            if product.product_availability:
                product_frame = tk.Frame(scrollable_frame, bg="#FFFFFF", bd=1, relief=tk.SOLID)
                product_frame.pack(fill=tk.X, pady=5, padx=5)

                product_info = f"ID: {product.product_id}, Name: {product.product_name}, Price: ${product.product_price:.2f}, Type: {product.product_type}, Rate: {product.product_rate}"
                tk.Label(product_frame, text=product_info, font=("Helvetica", 12), bg="#FFFFFF").pack(side=tk.LEFT, padx=10)

                add_button = tk.Button(product_frame, text="Add to Cart", font=("Helvetica", 12), bg="#4CAF50", fg="#FFFFFF",
                                       command=lambda p=product: self.add_to_cart(p))
                add_button.pack(side=tk.RIGHT, padx=10)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(search_frame, text="Back", command=self.logged_in_menu, **button_style).pack(pady=10)


# ////////////////////////////////////////////////////////

    def search_product(self):
        product_id = self.product_id_entry.get()
        product = self.system.logged_in_user.find_product(product_id)

        if product:
            self.display_product(product)

        else:
            messagebox.showerror("Error", "Product not found or unavailable")

# ////////////////////////////////////////////////////////

    def display_product(self, product):
        self.clear_screen()
        
        cart_frame = tk.Frame(self.root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
        cart_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(cart_frame, text="Product", font=("Helvetica", 18, "bold"), bg="#F0F0F0").pack(pady=10)

        product_frame = tk.Frame(cart_frame, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        product_frame.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(product_frame, text=f"ID: {product.product_id}", font=("Helvetica", 12), width=10, anchor='w', bg="#FFFFFF").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.Label(product_frame, text=f"Name: {product.product_name}", font=("Helvetica", 12), width=40, anchor='w', bg="#FFFFFF").grid(row=0, column=1, sticky='w', padx=5, pady=2)
        tk.Label(product_frame, text=f"Price: ${product.product_price:.2f}", font=("Helvetica", 12), width=20, anchor='w', bg="#FFFFFF").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        tk.Label(product_frame, text=f"Type: {product.product_type}", font=("Helvetica", 12), width=20, anchor='w', bg="#FFFFFF").grid(row=0, column=3, sticky='w', padx=5, pady=2)
        tk.Label(product_frame, text=f"Rate: {product.product_rate}", font=("Helvetica", 12), width=10, anchor='w', bg="#FFFFFF").grid(row=0, column=4, sticky='w', padx=5, pady=2)
        availability_text = "Available" if product.product_availability else "Not Available"
        availability_color = "#00FF00" if product.product_availability else "#FF0000"
        tk.Label(product_frame, text=f"{availability_text}", font=("Helvetica", 12), width=20, anchor='w', bg="#FFFFFF", fg=availability_color).grid(row=0, column=5, sticky='w', padx=5, pady=2)

        tk.Button(self.root, text="Add to Cart", command=lambda: self.add_to_cart(product)).pack()
        tk.Button(self.root, text="Back", command=self.search_product_screen).pack()

# ////////////////////////////////////////////////////////

    def add_to_cart(self, product):
        self.system.logged_in_user.add_product_to_cart(product.product_id)
        messagebox.showinfo("Success", "Product added to cart")
        self.logged_in_menu()

# ////////////////////////////////////////////////////////

    def proceed_cart(self):
        if len(self.system.logged_in_user.shopping_cart.products_id) == 0:
            messagebox.showinfo("Error", "Your shopping cart is empty!")
            return

        else:
            self.display_cart()

        if self.system.logged_in_user.proceed_cart():
            messagebox.showinfo("Success", "Payment successful")

        else:
            messagebox.showerror("Error", "Not enough money!")

# ////////////////////////////////////////////////////////

    def charge_wallet_screen(self):
        self.clear_screen()

        charge_frame = tk.Frame(self.root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
        charge_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(charge_frame, text="Charge Wallet", font=("Helvetica", 16)).pack(pady=10)

        tk.Label(charge_frame, text="Charge Amount", font=("Helvetica", 14), bg="#F0F0F0").pack(pady=5)
        self.charge_amount_entry = tk.Entry(charge_frame, font=("Helvetica", 14), bd=2, relief=tk.SUNKEN)
        self.charge_amount_entry.pack(pady=5)

        button_style = {"font": ("Helvetica", 14), "bg": "#4CAF50", "fg": "#FFFFFF", "relief": tk.RAISED, "bd": 2, "padx": 10, "pady": 5}

        tk.Button(charge_frame, text="Charge", command=self.charge_wallet, **button_style).pack(pady=10)
        tk.Button(charge_frame, text="Back", command=self.logged_in_menu, **button_style).pack(pady=10)

# ////////////////////////////////////////////////////////

    def charge_wallet(self):
        amount = self.charge_amount_entry.get()

        try:
            amount = float(amount)

            if amount > 0:
                self.system.logged_in_user.charge_wallet(amount)
                messagebox.showinfo("Success", "Wallet charged successfully")

            else:
                messagebox.showerror("Error", "Amount must be positive")

        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

# ////////////////////////////////////////////////////////

    def display_cart(self):
        self.clear_screen()

        cart_products = self.system.logged_in_user.shopping_cart.products_id

        if not cart_products:
            tk.Label(self.root, text="Shopping cart is empty", font=("Helvetica", 14), fg="#FF0000").pack(pady=20)

        else:
            # Create a frame for the cart
            cart_frame = tk.Frame(self.root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
            cart_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

            # Add a title for the shopping cart
            tk.Label(cart_frame, text="Shopping Cart", font=("Helvetica", 18, "bold"), bg="#F0F0F0").pack(pady=10)

            for product_id in cart_products:
                product = self.system.logged_in_user.find_product(product_id)
                if product:
                    product_frame = tk.Frame(cart_frame, bg="#FFFFFF", bd=1, relief=tk.SOLID)
                    product_frame.pack(fill=tk.X, pady=5, padx=5)

                    tk.Label(product_frame, text=f"ID: {product.product_id}", font=("Helvetica", 12), width=10, anchor='w', bg="#FFFFFF").grid(row=0, column=0, sticky='w', padx=5, pady=2)
                    tk.Label(product_frame, text=f"Name: {product.product_name}", font=("Helvetica", 12), width=40, anchor='w', bg="#FFFFFF").grid(row=0, column=1, sticky='w', padx=5, pady=2)
                    tk.Label(product_frame, text=f"Price: ${product.product_price:.2f}", font=("Helvetica", 12), width=20, anchor='w', bg="#FFFFFF").grid(row=0, column=2, sticky='w', padx=5, pady=2)
                    tk.Label(product_frame, text=f"Type: {product.product_type}", font=("Helvetica", 12), width=20, anchor='w', bg="#FFFFFF").grid(row=0, column=3, sticky='w', padx=5, pady=2)
                    tk.Label(product_frame, text=f"Rate: {product.product_rate}", font=("Helvetica", 12), width=10, anchor='w', bg="#FFFFFF").grid(row=0, column=4, sticky='w', padx=5, pady=2)

        tk.Button(self.root, text="Back", command=self.logged_in_menu, bg="#000000", fg="#FFFFFF", font=("Helvetica", 12)).pack(pady=10)

# ////////////////////////////////////////////////////////

    def remove_product_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Remove Product from Cart", font=("Helvetica", 16)).pack(pady=10)

        tk.Label(self.root, text="Product ID").pack(pady=10)
        self.remove_product_id_entry = tk.Entry(self.root)
        self.remove_product_id_entry.pack()

        tk.Button(self.root, text="Remove", command=self.remove_product).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.logged_in_menu).pack(pady=10)

# ////////////////////////////////////////////////////////

    def remove_product(self):
        product_id = self.remove_product_id_entry.get()

        if product_id:
            success = self.system.logged_in_user.remove_product(product_id)

            if success:
                messagebox.showinfo("Success", "Product removed from cart")

            else:
                messagebox.showerror("Error", "Product not found in cart")

        else:
            messagebox.showerror("Error", "Please enter a product ID")

# ////////////////////////////////////////////////////////

    def show_wallet_balance_screen(self):
        self.clear_screen()

        balance = self.system.logged_in_user.wallet_balance
        tk.Label(self.root, text="Wallet Balance", font=("Helvetica", 16)).pack(pady=10)
        tk.Label(self.root, text=f"Your wallet balance is: ${balance:.2f}", font=("Helvetica", 14)).pack(pady=20)

        tk.Button(self.root, text="Back", command=self.logged_in_menu).pack(pady=10)

# ////////////////////////////////////////////////////////

    def logout(self):
        self.system.logged_in_user = None
        self.login_screen()

# ////////////////////////////////////////////////////////

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

#  -------------------------------------------------------------------------  

# initializing UI ----------------------------------------------------------

# if you don't want to use UI uncomment below lines
if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineShopUI(root)
    root.mainloop()


