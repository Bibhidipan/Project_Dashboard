import flet as ft
import datetime
import psycopg2
from psycopg2 import sql
import math

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
        self.page.window_max_height = 800
        self.page.window_max_width = 400
        self.page.window_resizable = False
        self.page.padding=0
        self.page.theme_mode = "dark"
        AccentColour=["#0582f0","#2509b0","#4c09b0","#8a05f0","#8309b0","#551d80","#2c0f42"]

        Gradient_Background = ft.Container(
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, -1.25),
                radius=1.4,
                # gradient=ft.LinearGradient(
                # begin=ft.alignment.top_left,
                # end=ft.Alignment(0.8, 1),
                colors= AccentColour
    
            ),
            width=self.page.window_width,
            height=self.page.window_height,
            padding=10,
            margin=0,
            expand=True
        )

        
        self.Task = ft.Container(content=ft.TextField(
            hint_text="Enter The Task...", text_style=ft.TextStyle(color="a0cafd"), text_align="Left", color="a0cafd", border_color=ft.colors.TRANSPARENT),
            border=ft.Border( bottom=ft.BorderSide(1, ft.colors.WHITE)),
        border_radius=ft.border_radius.all(0),
        padding=ft.padding.only(bottom=5),)


        self.Priority = ft.Dropdown(
                    hint_text="Priority",
                    icon=ft.icons.PRIORITY_HIGH,
                    width=120,
                    options=[
                        ft.dropdown.Option("High"),
                        ft.dropdown.Option("Medium"),
                        ft.dropdown.Option("Low")
                    ],
                    filled=None,
                    border_color=ft.colors.TRANSPARENT,
                    hint_style=ft.TextStyle(color="a0cafd"),
                    text_style=ft.TextStyle(color="a0cafd", weight=ft.FontWeight.BOLD),  # Changed text color to black
                    bgcolor=ft.colors.TRANSPARENT,
                    focused_bgcolor=ft.colors.TRANSPARENT  # Changed focused background color
                )


        def Date_Select(e):
            self.DateSelect.value = e.control.value.strftime('%Y-%m-%d')
            self.DateSelect.text = self.DateSelect.value
            self.DateSelect.update()

        def open_date_picker(e):
            date_picker = ft.DatePicker(value=datetime.datetime.now(),on_change=Date_Select)
            self.page.dialog = date_picker
            self.page.dialog.open = True
            self.page.update()

        self.DateSelect = ft.ElevatedButton(text="Target Date", icon=ft.icons.CALENDAR_MONTH, on_click=open_date_picker, bgcolor= ft.colors.TRANSPARENT,elevation=0)


        self.TabProperties = ft.Tabs(selected_index=0, animation_duration=300, divider_height=0, indicator_padding=0, scrollable=True,
            tabs=[
                ft.Tab(text="Pending", icon=ft.icons.DENSITY_SMALL, content=ft.ListView(expand=True, spacing=10, padding=10)),
                ft.Tab(text="Ongoing", icon=ft.icons.PENDING_ACTIONS, content=ft.ListView(expand=True, spacing=10, padding=10)),
                ft.Tab(text="Completed", icon=ft.icons.DONE_ALL, content=ft.ListView(expand=True, spacing=10, padding=10))
            ], expand=1
        )

        # self.page.add(self.TabProperties)
        page.add(
            ft.Stack(
                controls=[
                    # Base background layer with gradient
                    Gradient_Background,
                    
                    # Column containing the two containers stacked vertically
                    ft.Column(
                        controls=[
                            # First container: Task input and priority selection
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(controls=[self.Task,
                                                        ft.FloatingActionButton(
                                                        icon=ft.icons.ADD, 
                                                        on_click=self.Add_Task, 
                                                        bgcolor=ft.colors.TRANSPARENT, 
                                                        elevation=0)], 
                                                        alignment=ft.MainAxisAlignment.CENTER),
                                        ft.Row(
                                            controls=[
                                                self.Priority,
                                                self.DateSelect,
                                                
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=10,
                                ),
                                padding=ft.padding.all(10),
                                margin=0,
                                alignment=ft.alignment.top_center,
                            ),
                            
                            # Second container: Tab properties (lists of tasks)
                            ft.Container(
                                content=self.TabProperties,
                                expand=True,
                                padding=ft.padding.all(10),
                                margin=0,
                            )
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,  # Stack the containers starting from the top
                        spacing=0,  # No spacing between containers
                    )
                ],
                expand=True,  # Ensures the Stack takes the full available space
            )
        )
        self.load_tasks()



    def Add_Task(self, e):
    # Access the value of the TextField directly
        task_value = self.Task.content.value if self.Task.content else ""
        
        # Access the value of the Dropdown
        priority_value = self.Priority.value
        
        # Access the text of the ElevatedButton for the date
        date_value = self.DateSelect.text if self.DateSelect.text != "Target Date" else ""

        if not task_value or not priority_value or not date_value:
            PopUp(self.page, "Error", "Please Fill All the fields Correctly")
            return
        
        try:
            Connection_Var = Databse_Connection()
            MyCursor = Connection_Var.cursor()
            MyCursor.execute("INSERT INTO data (Task, Priority, Target_Date, Status) VALUES (%s, %s, %s, %s)",
                            (task_value, priority_value, date_value, "Pending"))
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
        self.DateSelect.text = "Target Date"
        # self.Task.focus()
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
            task_id, Task, Priority, DateSelect, Status = task

            if Status == "Pending":
                gradient_colors = ["0xff1f005c", "0xff5b0060", "0xff870160", "0xffac255e", "0xffca485c", "0xffe16b5c", "0xfff39060", "#f79f5c"]
                                # gradient_colors =["#fa4402", "#db4712", "#ba441a", "#ba441a", "#ba2a1a", "#7a150a", "#57110a", "#300905"]
            elif Status == "Ongoing":
                gradient_colors = ["#2707f5", "#2f17cf", "#3422a8", "#332687", "#261e57", "#1a1533", "#0a0912"]
            elif Status == "Completed":
                gradient_colors = ["#04662e", "#1f9456", "#1f7346", "#1d5738", "#163826"]
            else:  # Default gradient if Status is unknown or "Delete"
                gradient_colors = ["#808080", "#a9a9a9"]

            if Status == "Pending":
                card_opacity = 1.0  # Fully opaque
            elif Status == "Ongoing":
                card_opacity = 0.8  # Slightly transparent
            elif Status == "Completed":
                card_opacity = 0.6  
            
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
                                    ], border_radius=30, filled=False, border_color=ft.colors.TRANSPARENT, 
                                    # bgcolor=ft.colors.TRANSPARENT,
                                    on_change=lambda e, task_id=task_id: self.Update_Task_Status(task_id, e.control.value)
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.MainAxisAlignment.CENTER),
                            ft.Text(f"Target Date: {DateSelect}", text_align="start"),
                            
                        ],
                        spacing=2
                    ), 
                    gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.Alignment(0.8, 1),
                colors=gradient_colors,
                tile_mode=ft.GradientTileMode.MIRROR,rotation=math.pi / 3,),
                    padding=10,  # Apply padding here
                    width=380,
                    border_radius=10  # Slightly less than the card's width to accommodate padding
                ),
                elevation=2,
                width=400,
                # opacity=card_opacity
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

ft.app(target=main)
