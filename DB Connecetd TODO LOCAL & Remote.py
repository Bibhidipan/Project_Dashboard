from flet import*
import flet as ft
import datetime
import pymysql
import psycopg2
from email_validator import validate_email, EmailNotValidError


# def create_text_field(self, label, height=40, password=False):
#     return ft.TextField(
#         label=label, 
#         color="Blue", 
#         cursor_color="Green", 
#         height=height,
#         password=password
#     )

# def create_button(self, text, on_click):
#     return ft.ElevatedButton(text=text, on_click=on_click)

# def open_date_picker(self, e):
#     date_picker = ft.DatePicker(value=datetime.datetime.now(), on_change=self.Date_Select)
#     self.page.dialog = date_picker
#     self.page.dialog.open = True
#     self.page.update()

# def Date_Select(self, e):
#     self.DateSelect.value = e.control.value.strftime('%Y-%m-%d')
#     self.DateSelect.update()

# def update_ui(self):
#     for component in [self.Username, self.Email, self.Password, self.ConfirmPassword, self.DateSelect, self.SecurityQS, self.Answer]:
#         component.update()


def PopUp(page, title, message):
    def ClosePopUp(e):
        page.dialog.open = False
        page.update()
    Dialogue = ft.AlertDialog(
        title=ft.Text(title), 
        content=ft.Text(message), 
        actions=[ft.TextButton("Ok", on_click=ClosePopUp)])
    page.dialog = Dialogue
    page.dialog.open = True
    page.update()


def Databse_Connection():
    return psycopg2.connect(
            dbname="neondb", 
            user= "neondb_owner", 
            password= "y0ixLQr5cejH", 
            host="ep-raspy-limit-a15i1ow4.ap-southeast-1.aws.neon.tech", 
            port="5432")

def Create_Database():
    try:
        connection = psycopg2.connect(
            dbname="neondb", 
            user= "neondb_owner", 
            password= "y0ixLQr5cejH", 
            host="ep-raspy-limit-a15i1ow4.ap-southeast-1.aws.neon.tech", 
            port="5432")
        
        cursor = connection.cursor()
        cursor.execute("create table if not exists data(id SERIAL PRIMARY KEY, Task TEXT, Priority TEXT, Target_Date DATE, Status TEXT)")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Database creation failed: {e}")



class ToDo_APP:
    def __init__(self, page):
        self.page = page
        self.page.title = "The Workflow Enhancer"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        self.page.window_height = 800
        self.page.window_width = 400
        self.page.window_resizable = False
        self.page.theme_mode = "dark"
        
        self.Task = ft.TextField(hint_text="Enter The Task", text_align="Left", width=380)
        self.Priority = ft.Dropdown(hint_text="Priority", 
                                    width=100, 
                                    options=[ft.dropdown.Option("High"), 
                                    ft.dropdown.Option("Medium"), 
                                    ft.dropdown.Option("Low")])

        def Date_Select(e):
            self.DateSelect.value = e.control.value.strftime('%Y-%m-%d')
            self.DateSelect.text = self.DateSelect.value
            self.DateSelect.update()

        def open_date_picker(e):
            date_picker = ft.DatePicker(value=datetime.datetime.now(),on_change=Date_Select)
            self.page.dialog = date_picker
            self.page.dialog.open = True
            self.page.update()

        self.DateSelect = ft.ElevatedButton(text="Target Date", icon=ft.icons.CALENDAR_MONTH, on_click=open_date_picker)

        page.add(self.Task, 
                ft.Row([
                    self.Priority, 
                    self.DateSelect, ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.Add_Task)]))

        self.TabProperties = ft.Tabs(selected_index=0, animation_duration=300, divider_height=0, indicator_padding=0, scrollable=True,
            tabs=[
                ft.Tab(text="Pending", icon=ft.icons.DENSITY_SMALL, content=ft.ListView(expand=True, spacing=10, padding=10)),
                ft.Tab(text="Ongoing", icon=ft.icons.PENDING_ACTIONS, content=ft.ListView(expand=True, spacing=10, padding=10)),
                ft.Tab(text="Completed", icon=ft.icons.DONE_ALL, content=ft.ListView(expand=True, spacing=10, padding=10))
            ], expand=1
        )

        self.page.add(self.TabProperties)
        self.load_tasks()

    def Add_Task(self, e):
        if not self.Task.value or not self.Priority.value or self.Target_Date.value == "Target Date":
            PopUp(self.page, "Error", "Please Fill All the fields Correctly")
            return
        try:
            Connection_Var = Databse_Connection()
            MyCursor = Connection_Var.cursor()
            MyCursor.execute("INSERT INTO data (Task, Priority, Target_Date, Status) VALUES (%s, %s, %s, %s)",
                            (self.Task.value, self.Priority.value, self.Target_Date.value, "Pending"))
            Connection_Var.commit()
            MyCursor.close()
            Connection_Var.close()
            PopUp(self.page, "Success", "Task Added Successfully")
            self.clear_inputs()
            self.load_tasks()
        except Exception as e:
            PopUp(self.page, "Error", f"Failed to add Task {e}")

    def clear_inputs(self):
        self.Task.value = ""
        self.Priority.value = None
        self.Target_Date.value = "Target Date"
        self.DateSelect.text = "Target Date"
        self.Task.focus()
        self.Task.update()
        self.DateSelect.update()
        self.page.update()

    def load_tasks(self):
        tasks = self.fetch_data()
        pending_tasks = [task for task in tasks if task[4] == "Pending"]
        ongoing_tasks = [task for task in tasks if task[4] == "Ongoing"]
        completed_tasks = [task for task in tasks if task[4] == "Completed"]
        self.update_tab_content(0, pending_tasks)
        self.update_tab_content(1, ongoing_tasks)
        self.update_tab_content(2, completed_tasks)

    def update_tab_content(self, tab_index, tasks):
        tab_content = self.TabProperties.tabs[tab_index].content

        tab_content.controls.clear()
        for task in tasks:
            task_id, Task, Priority, Target_Date, Status = task
            
            # Create a card for each task
            task_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Task: {Task}", size=16, weight="bold", text_align="start"),
                            ft.Row([
                                ft.Text(f"Priority: {Priority}", size=14, text_align="start"),
                                ft.Dropdown(
                                    width=120,
                                    value=Status,
                                    options=[
                                        ft.dropdown.Option("Pending"),
                                        ft.dropdown.Option("Ongoing"),
                                        ft.dropdown.Option("Completed"),
                                        ft.dropdown.Option("Delete")
                                    ],
                                    on_change=lambda e, task_id=task_id: self.Update_Task_Status(task_id, e.control.value)
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.MainAxisAlignment.CENTER),
                            ft.Text(f"Target Date: {Target_Date}", text_align="start"),
                            
                        ],
                        spacing=2
                    ),
                    padding=10,  # Apply padding here
                    width=380  # Slightly less than the card's width to accommodate padding
                ),
                elevation=2,
                width=400
            )

            tab_content.controls.append(task_card)

        tab_content.update()

    def Update_Task_Status(self, task_id, new_Status):
        try:
            if new_Status == "Delete":
                connection = Databse_Connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM data WHERE id = %s", (task_id,))
                connection.commit()
                connection.close()
                self.load_tasks()
            else:
                Connection_var = Databse_Connection()
                MyCursor = Connection_var.cursor()
                MyCursor.execute("UPDATE data SET Status = %s WHERE id = %s", (new_Status, task_id))
                Connection_var.commit()
                MyCursor.close()
                Connection_var.close()
                self.load_tasks()
        except Exception as e:
            PopUp(self.page, "Error", f"Failed to update task Status: {e}")

    def fetch_task_id(self, task_label):
        try:
            Connection_var = Databse_Connection()
            MyCursor = Connection_var.cursor()
            MyCursor.execute("SELECT id FROM data WHERE Task = %s", (task_label,))
            task_id = MyCursor.fetchone()
            MyCursor.close()
            Connection_var.close()
            return task_id[0] if task_id else None
        except Exception as e:
            PopUp(self.page, "Error", f"Failed to fetch task ID: {e}")
            return None

    def fetch_data(self):
        try:
            Connection_Var = Databse_Connection()
            MyCursor = Connection_Var.cursor()
            MyCursor.execute("SELECT id, Task, Priority, Target_Date, Status from data")
            Rows = MyCursor.fetchall()
            Priority_Level = {"High": 1, "Medium": 2, "Low": 3}
            Sorted_Rows = sorted(Rows, key=lambda DBColumn: (DBColumn[3], Priority_Level.get(DBColumn[2], 4)))
            MyCursor.close()
            Connection_Var.close()
            return Sorted_Rows
        except Exception as e:
            PopUp(self.page, "Error", f"Failed to fetch Tasks {e}")

    def Create_data(self):
        try:
            Connection_Var = Databse_Connection()
            MyCursor = Connection_Var.cursor()
            MyCursor.execute("create table if not exists data(id SERIAL PRIMARY KEY, Task TEXT, Priority TEXT, Target_Date DATE, status TEXT)")
            Connection_Var.close()
        except Exception as e:
            PopUp(self.page, "Error", f"Database Creation Failed {e}")

def main(page: ft.Page):
    Create_Database()
    app = ToDo_APP(page)
    app.Create_data()





class Authentication_Page:
    def __init__(self, page):
        self.page = page
        page.window.height = 800
        page.window.width = 400
        self.Login_Page(page)

    def Login_Page(self, page):
        self.Page_Heading = ft.Text(
            value="Welcome!!", 
            color="green", 
            text_align=ft.TextAlign.CENTER,
            font_family="Impact", 
            size=40, 
            weight=ft.FontWeight.BOLD, 
            italic=False
        )
        self.Email = ft.TextField(
            hint_text="Email", 
            color="Blue", 
            cursor_color="Green"
        )
        self.Password = ft.TextField(label="Password", password=True)
        self.Login_Button = ft.ElevatedButton("Login", on_click=self.Login)
        self.Forgot_Password_Button = ft.TextButton("Forgot Password?", on_click=self.ToForgotPassword)
        self.SignUp_Button = ft.TextButton("Don't have an account?", on_click=self.ToSignUp)
        page.add(
            ft.Row([self.Page_Heading], alignment=ft.MainAxisAlignment.CENTER), 
            self.Email, 
            self.Password, 
            self.Login_Button,
            self.Forgot_Password_Button,
            ft.Row([self.SignUp_Button], alignment=ft.MainAxisAlignment.CENTER)
        )

    def ForgotPassWordPage(self, page):
        self.Page_Heading = ft.Text(
            value="Reset Password", 
            color="green", 
            text_align=ft.TextAlign.CENTER,
            font_family="Impact", 
            size=40, 
            weight=ft.FontWeight.BOLD, 
            italic=False
        )
        self.Username = ft.TextField(
            label="Username/Name", 
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Email = ft.TextField(
            label="Email", 
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Password = ft.TextField(
            label="NewPassword",
            color="Blue", 
            cursor_color="Green", 
            height=40,
            password=True
        )
        self.ConfirmPassword = ft.TextField(
            label="ConfirmPassword",
            color="Blue", 
            cursor_color="Green", 
            height=40,
            password=True
        )

        def Date_Select(e):
            self.DateSelect.value = e.control.value.strftime('%Y-%m-%d')
            self.DateSelect.text = self.DateSelect.value
            self.DateSelect.update()

        def open_date_picker(e):
            date_picker = ft.DatePicker(value=datetime.datetime.now(), on_change=Date_Select)
            self.page.dialog = date_picker
            self.page.dialog.open = True
            self.page.update()

        self.DateSelect = ft.ElevatedButton(text="D.O.B", icon=ft.icons.CALENDAR_MONTH, on_click=open_date_picker)

        self.SecurityQS = ft.Dropdown(hint_text="Choose The Security Question",
            options=[
                ft.dropdown.Option("Your First Mobile Brand"),
                ft.dropdown.Option("Your First School Name"),
                ft.dropdown.Option("Your Favourite Pet Name"),
            ]
        )
        self.Answer = ft.TextField(
            label="Answer",
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Reset_Password_Button = ft.ElevatedButton("Reset Password", on_click=self.Reset_Password)
        self.BackToLogin_Button = ft.ElevatedButton("Back To Login", on_click=self.BackToLogin)
        page.add(
            ft.Row([self.Page_Heading], alignment=ft.MainAxisAlignment.CENTER), 
            self.Username, 
            self.Email,
            self.Password, 
            self.ConfirmPassword,
            self.DateSelect,
            self.SecurityQS,
            self.Answer,
            self.Reset_Password_Button,
            self.BackToLogin_Button
        )

    def SignUpPage(self, page):
        self.Page_Heading = ft.Text(
            value="User Registration", 
            color="green", 
            text_align=ft.TextAlign.CENTER,
            font_family="Impact", 
            size=40, 
            weight=ft.FontWeight.BOLD, 
            italic=False
        )
        self.Username = ft.TextField(
            label="Username/Name", 
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Email = ft.TextField(
            label="Email", 
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Password = ft.TextField(
            label="Password",
            color="Blue", 
            cursor_color="Green", 
            height=40,
            password=True
        )
        self.ConfirmPassword = ft.TextField(
            label="ConfirmPassword",
            color="Blue", 
            cursor_color="Green", 
            height=40,
            password=True
        )

        def Date_Select(e):
            self.DateSelect.value = e.control.value.strftime('%Y-%m-%d')
            self.DateSelect.text = self.DateSelect.value
            self.DateSelect.update()

        def open_date_picker(e):
            date_picker = ft.DatePicker(value=datetime.datetime.now(), on_change=Date_Select)
            self.page.dialog = date_picker
            self.page.dialog.open = True
            self.page.update()

        self.DateSelect = ft.ElevatedButton(text="D.O.B", icon=ft.icons.CALENDAR_MONTH, on_click=open_date_picker)

        self.SecurityQS = ft.Dropdown(hint_text="Choose The Security Question",
            options=[
                ft.dropdown.Option("Your First Mobile Brand"),
                ft.dropdown.Option("Your First School Name"),
                ft.dropdown.Option("Your Favourite Pet Name"),
            ]
        )
        self.Answer = ft.TextField(
            label="Answer",
            color="Blue", 
            cursor_color="Green", 
            height=40
        )
        self.Designation = ft.Dropdown(hint_text="Choose Your Organizational Position",
            options=[
                ft.dropdown.Option("Cheif"),
                ft.dropdown.Option("Head"),
                ft.dropdown.Option("Senior Manager"),
                ft.dropdown.Option("Manager"),
                ft.dropdown.Option("Asst. Manager"),
                
            ]
        )
        self.SignUp_Button = ft.ElevatedButton("SignUp", on_click=self.SignUp)
        self.BackToLogin_Button = ft.ElevatedButton("Back To Login", on_click=self.BackToLogin)
        page.add(
            ft.Row([self.Page_Heading], alignment=ft.MainAxisAlignment.CENTER), 
            self.Username, 
            self.Email,
            self.Password, 
            self.ConfirmPassword,
            self.DateSelect,
            self.SecurityQS,
            self.Answer,
            self.Designation,
            self.SignUp_Button,
            self.BackToLogin_Button
        )

    def PopUp(self, page, title, message):
        def ClosePopUp(e):
            page.dialog.open = False
            page.update()
        Dialogue = ft.AlertDialog(
            title=ft.Text(title), 
            content=ft.Text(message), 
            actions=[ft.TextButton("Ok", on_click=ClosePopUp)]
        )
        page.dialog = Dialogue
        page.dialog.open = True
        page.update()

    def ToForgotPassword(self, e):
        self.page.clean()
        self.ForgotPassWordPage(self.page)

    def ToSignUp(self, e):
        self.page.clean()
        self.SignUpPage(self.page)

    def BackToLogin(self, e):
        self.page.clean()
        self.Login_Page(self.page)

    def Reset_Password(self, e):
        print("XYZ")

    def calculate_age(self, dob_str):
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age >= 18:
            return True
        return False

    def Name_varify(self, Username):
        if not Username.strip():
            return False
        for j in Username:
            if not (j.isalpha() or j.isspace()):
                return False
        return True

    def Email_varify(self, Email):
        try:
            valid = validate_email(Email)
            email = valid.email
            return True
        except EmailNotValidError as e:
            return False

    def Password_verify(self, Password):
        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False
        if 12 >= len(Password) >= 8:
            for i in Password:
                if i.isupper():
                    has_upper = True
                elif i.islower():
                    has_lower = True
                elif i.isdigit():
                    has_digit = True
                else:
                    has_special = True
        if has_upper and has_lower and has_digit and has_special:
            return True
        return False

    def CPassword_verify(self, ConfirmPassword, Password):
        if ConfirmPassword == Password:
            return True
        return False

    def SignUp(self, e):
        if (self.Username.value == "" 
            or self.Email.value == "" 
            or self.Password.value == "" 
            or self.ConfirmPassword.value == "" 
            or self.DateSelect.value == ""
            or self.Answer.value == ""
            or self.Designation.value == ""
        ):
            self.PopUp(self.page, "Error", "Fill All the fields correctly")

        elif not self.Name_varify(self.Username.value):
            self.PopUp(self.page, "Error","Name Field should only have Alphabetical Characters")
        elif not self.Email_varify(self.Email.value):
            self.PopUp(self.page,"Error","Enter Valid Email Address")
        elif not self.Password_verify(self.Password.value):
            self.PopUp(self.page, "Error",
                "1.Password Length Must be between 8-12 characters, 2.Password must have at least 1 Capital, 1 Small, 1 Digit & 1 Special Character")
        elif not self.CPassword_verify(self.ConfirmPassword.value, self.Password.value):
            self.PopUp(self.page,"Error","Password & Confirm Password don't match")
        elif not self.calculate_age(self.DateSelect.text):
            self.PopUp(self.page, "Error", "You must be at least 18 years old to register")
        else:
            try:
                Connection_var = pymysql.connect(host="localhost", user="root", password="SQL@2022bibhi")
                MyCursor = Connection_var.cursor()
            except Exception as e:
                self.PopUp(self.page, "Error", "Some Error Occurred")
                return
            try:
                query = "create database if not exists userdata"
                MyCursor.execute(query)
                query = "use userdata"
                MyCursor.execute(query)
                query = (
                    "create table if not exists data ("
                    "id int auto_increment primary key not null, "
                    "Name varchar(50), Email varchar(50), Password varchar (12), "
                    "DOB varchar(10), SecurityQS varchar (100), Answer varchar(30), Designation varchar (100))"
                )
                MyCursor.execute(query)
            except Exception as e:
                self.PopUp(self.page, "Error", "Some Error Occurred During Database Setup")
                return

            try:
                query = (
                    "insert into data(Name, Email, Password, DOB, SecurityQS, Answer, Designation) "
                    "values(%s, %s, %s, %s, %s, %s, %s)"
                )
                MyCursor.execute(query, (
                    self.Username.value, 
                    self.Email.value, 
                    self.Password.value, 
                    self.DateSelect.text, 
                    self.SecurityQS.value, 
                    self.Answer.value,
                    self.Designation.value
                ))
                Connection_var.commit()
                Connection_var.close()
                self.PopUp(self.page, "Success", "Signup Successful!!")
                self.Entry_clear()
            except Exception as e:
                self.PopUp(self.page, "Error", "Some Error Occurred During Data Insertion")

    def Reset_Password(self, e):
        if (self.Username.value == "" 
            or self.Email.value == "" 
            or self.Password.value == "" 
            or self.ConfirmPassword.value == "" 
            or self.DateSelect.value == ""
            or self.Answer.value == ""
        ):
            self.PopUp(self.page, "Error", "Fill All the fields correctly")

        elif not self.Name_varify(self.Username.value):
            self.PopUp(self.page, "Error", "Name Field should only have Alphabetical Characters")
        elif not self.Email_varify(self.Email.value):
            self.PopUp(self.page, "Error", "Enter Valid Email Address")
        elif not self.Password_verify(self.Password.value):
            self.PopUp(self.page, "Error",
                "1. Password Length Must be between 8-12 characters, 2. Password must have at least 1 Capital, 1 Small, 1 Digit & 1 Special Character")
        elif not self.CPassword_verify(self.ConfirmPassword.value, self.Password.value):
            self.PopUp(self.page, "Error", "Password & Confirm Password don't match")
        elif not self.calculate_age(self.DateSelect.text):
            self.PopUp(self.page, "Error", "Userdata not registered")
        else:
            try:
                Connection_var = pymysql.connect(host="localhost", user="root", password="SQL@2022bibhi", database="userdata")
                MyCursor = Connection_var.cursor()
            except Exception as e:
                self.PopUp(self.page, "Error", "Some Error Occurred during Database connection")
                return

            # Verify user exists
            query = """
                SELECT * FROM data 
                WHERE Name = %s 
                AND Email = %s 
                AND DOB = %s 
                AND SecurityQS = %s 
                AND Answer = %s
            """
            MyCursor.execute(query, (
                self.Username.value, 
                self.Email.value, 
                self.DateSelect.text, 
                self.SecurityQS.value, 
                self.Answer.value
            ))
            row = MyCursor.fetchone()
            if row is None:
                self.PopUp(self.page, "Error", "User Doesn't Exist in database")
            else:
                # try:
                    # Update password
                    query = """
                        UPDATE data 
                        SET Password = %s 
                        WHERE Name = %s 
                        AND Email = %s 
                        AND DOB = %s 
                        AND SecurityQS = %s 
                        AND Answer = %s
                    """
                    MyCursor.execute(query, (
                        self.Password.value,
                        self.Username.value, 
                        self.Email.value, 
                        self.DateSelect.text, 
                        self.SecurityQS.value, 
                        self.Answer.value
                    ))
                    Connection_var.commit()
                    Connection_var.close()
                    self.PopUp(self.page, "Welcome", "Password reset Successful, please login with new password")
                    self.Entry_clear()

    def Login(self, e):
        # print("working")
        if (self.Email.value=="" or self.Password.value==""): self.PopUp(self.page, "Error", "Fill All the fields correctly")
        else:
            try:
                Connection_var=pymysql.connect(host="localhost", user= "root", password= "SQL@2022bibhi")
                MyCursor=Connection_var.cursor()
            except: 
                self.PopUp(self.page, "Error", "Some Error Occured")
                return
            query="use userdata"
            MyCursor.execute(query)
            query= "SELECT * FROM data WHERE Email = %s AND Password = %s"
            MyCursor.execute(query,(self.Email.value, self.Password.value))
            row= MyCursor.fetchone()
            if row==None: self.PopUp(self.page, "Error", "Invalid Email or Password")
            else: 
                self.PopUp(self.page,"Welcome!", "Login Successful!!")
                # self.Email.value = ""
                # self.Password.value = ""
                # self.Email.update()
                # self.Password.update()
                self.page.clean()
                ToDo_APP(self.page)
                

    def Entry_clear(self):
        self.Username.value = ""
        self.Email.value = ""
        self.Password.value = ""
        self.ConfirmPassword.value = ""
        self.DateSelect.text = "D.O.B"
        self.SecurityQS.value = ""
        self.Answer.value = ""
        self.Username.update()
        self.Email.update()
        self.Password.update()
        self.ConfirmPassword.update()
        self.DateSelect.update()
        self.SecurityQS.update()
        self.Answer.update()

def main(page):
    page.title = "Login Page"
    Authentication_Page(page)

ft.app(target=main)




