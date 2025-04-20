import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
from tkcalendar import Calendar
import os
from dotenv import load_dotenv

class SalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Salon Management System")
        self.root.geometry("1200x700")


        # Color scheme
        self.colors = {
            "bg": "#fed0d1",       # Soft pink background
            "card": "#ffffff",     # White card
            "primary": "#ff6b81",  # Coral accent
            "text": "#ffffff",     # Dark text
            "light_text": "#666666" # Gray text

        }
    
        # Configure root window
        self.root.configure(bg=self.colors["bg"])
        
        # Initialize styles
        self._configure_styles()
    
        
        # MySQL Database connection
        load_dotenv()  # Loads secrets from .env file

        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),  # Default: localhost
            user=os.getenv("DB_USER", "salon_user"),  # Default: salon_user
            password=os.getenv("DB_PASSWORD"),  # No default! Must be in .env
            database=os.getenv("DB_NAME", "salon_management")
        )
        self.cursor = self.db.cursor()

        # Verify database is properly set up
        try:
            self.cursor.execute("SELECT 1 FROM users LIMIT 1")
        except mysql.connector.Error:
            messagebox.showerror(
                "Database Error", 
                "Database not initialized!\n\n"
                "Run:\n'mysql -u root -p < schema.sql'\n"
                "to set up the database."
            )
            self.root.destroy()
            return
        
        # Create tables if they don't exist
        self.create_tables()
        
        # Current user info
        self.current_user = None
        self.user_type = None
        
        # Show login screen
        self.show_login_screen()


    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _configure_styles(self):
        style = ttk.Style()
        
        # Card frame style
        style.configure("Login.TFrame",
                    background=self.colors["card"],
                    relief="raised",
                    borderwidth=2,
                    bordercolor="#e0e0e0")
        
        # Elegant button style
        style.configure("Pink.TButton",
                    background=self.colors["primary"],
                    foreground="white",
                    font=('Helvetica', 11, 'bold'),
                    padding=10,
                    borderwidth=0)
        
        style.map("Pink.TButton",
                background=[('active', '#e55c6c')])  # Darker coral on press
        
        # Modern entry fields
        style.configure("Pink.TEntry",
                    fieldbackground="white",
                    foreground=self.colors["text"],
                    bordercolor="#cccccc",
                    relief="solid",
                    padding=8,
                    font=('Helvetica', 10))
        
        # Label style
        style.configure("Pink.TLabel",
                    background=self.colors["card"],
                    foreground=self.colors["text"],
                    font=('Helvetica', 10))
        
        # Radiobutton style
        style.configure("Pink.TRadiobutton",
                    background=self.colors["card"],
                    foreground=self.colors["text"],
                    font=('Helvetica', 10))
        
    def show_login_screen(self):
        self.clear_window()
        
        # Main card with shadow effect
        login_card = ttk.Frame(self.root, style="Login.TFrame", padding=(40, 30))
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header with logo placeholder
        header_frame = ttk.Frame(login_card)
        header_frame.pack(pady=(0, 20))
        
        # Salon name with coral accent
        ttk.Label(header_frame,
                text="MySalon",
                font=('Helvetica', 24, 'bold'),
                foreground=self.colors["primary"],
                background=self.colors["card"]).pack()
        
        ttk.Label(header_frame,
                text="Management System",
                font=('Helvetica', 14),
                foreground=self.colors["light_text"],
                background=self.colors["card"]).pack()
        
        # User type selection
        self.login_type = tk.StringVar(value="customer")
        type_frame = ttk.Frame(login_card)
        type_frame.pack(pady=10)
        
        ttk.Radiobutton(type_frame,
                    text="Customer",
                    variable=self.login_type,
                    value="customer",
                    style="Pink.TRadiobutton").pack(side=tk.LEFT, padx=15)
        
        ttk.Radiobutton(type_frame,
                    text="Service Provider",
                    variable=self.login_type,
                    value="provider",
                    style="Pink.TRadiobutton").pack(side=tk.LEFT, padx=15)
        
        # Form fields
        form_frame = ttk.Frame(login_card)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame,
                text="Username:",
                style="Pink.TLabel").grid(row=0, column=0, pady=8, sticky="e")
        
        self.username_entry = ttk.Entry(form_frame, style="Pink.TEntry", width=25)
        self.username_entry.grid(row=0, column=1, pady=8, padx=10)
        
        ttk.Label(form_frame,
                text="Password:",
                style="Pink.TLabel").grid(row=1, column=0, pady=8, sticky="e")
        
        self.password_entry = ttk.Entry(form_frame, style="Pink.TEntry", show="•", width=25)
        self.password_entry.grid(row=1, column=1, pady=8, padx=10)
        
        # Action buttons
        btn_frame = ttk.Frame(login_card)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame,
                text="Login",
                style="Pink.TButton",
                command=self.login).pack(side=tk.LEFT, padx=10, ipadx=20)
        
        ttk.Button(btn_frame,
                text="Register",
                style="Pink.TButton",
                command=self.show_registration).pack(side=tk.LEFT, padx=10, ipadx=15)
        
    def login(self):
        """Authenticate user"""
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())
        user_type = self.login_type.get()
        
        try:
            self.cursor.execute(
                "SELECT id, name, user_type FROM users WHERE username = %s AND password = %s AND user_type = %s",
                (username, password, user_type)
            )
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = {
                    'id': user[0],
                    'name': user[1],
                    'type': user[2]
                }
                self.user_type = user_type
                
                if user_type == 'customer':
                    self.show_customer_dashboard()
                else:
                    self.show_provider_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during login: {err}")

    def show_registration(self):
        """Display registration form with elegant styling"""
        self.clear_window()
        
        # Main card with shadow effect (matching login style)
        reg_card = ttk.Frame(self.root, style="Login.TFrame", padding=(40, 30))
        reg_card.place(relx=0.5, rely=0.5, anchor="center")

        # Header with consistent branding
        header_frame = ttk.Frame(reg_card)
        header_frame.pack(pady=(0, 15))
        
        ttk.Label(header_frame,
                text="Create Account",
                font=('Helvetica', 20, 'bold'),
                foreground=self.colors["primary"],
                background=self.colors["card"]).pack()
        
        # User type selection with improved styling
        type_frame = ttk.Frame(reg_card)
        type_frame.pack(pady=(10, 15))
        
        self.reg_type = tk.StringVar(value="customer")
        ttk.Radiobutton(type_frame,
                    text="Customer",
                    variable=self.reg_type,
                    value="customer",
                    style="Pink.TRadiobutton").pack(side=tk.LEFT, padx=15)
        
        ttk.Radiobutton(type_frame,
                    text="Service Provider",
                    variable=self.reg_type,
                    value="provider",
                    style="Pink.TRadiobutton").pack(side=tk.LEFT, padx=15)
        
        # Form fields with consistent styling
        form_frame = ttk.Frame(reg_card)
        form_frame.pack(pady=10)
        
        fields = [
            ("Username:", "username"),
            ("Password:", "password", True),
            ("Confirm Password:", "confirm_password", True),
            ("Full Name:", "name"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Location:", "location")
        ]
        
        self.reg_entries = {}
        for i, field in enumerate(fields):
            ttk.Label(form_frame,
                    text=field[0],
                    style="Pink.TLabel").grid(row=i, column=0, pady=8, sticky="e")
            
            show = "•" if len(field) > 2 and field[2] else ""
            entry = ttk.Entry(form_frame,
                            style="Pink.TEntry",
                            show=show,
                            width=25)
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.reg_entries[field[1]] = entry
        
        # Action buttons with matching style
        btn_frame = ttk.Frame(reg_card)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame,
                text="Register",
                style="Pink.TButton",
                command=self.register).pack(side=tk.LEFT, padx=10, ipadx=20)
        
        ttk.Button(btn_frame,
                text="Back to Login",
                style="Pink.TButton",
                command=self.show_login_screen).pack(side=tk.LEFT, padx=10, ipadx=15)
        
        # Add subtle footer text
        ttk.Label(reg_card,
                text="All fields are required",
                style="Pink.TLabel",
                font=('Helvetica', 8)).pack(pady=(15, 0))

    def register(self):
        """Register new user"""
        if self.reg_entries['password'].get() != self.reg_entries['confirm_password'].get():
            messagebox.showerror("Error", "Passwords don't match")
            return
        
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, user_type, name, phone, email, location) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    self.reg_entries['username'].get(),
                    self.hash_password(self.reg_entries['password'].get()),
                    self.reg_type.get(),
                    self.reg_entries['name'].get(),
                    self.reg_entries['phone'].get(),
                    self.reg_entries['email'].get(),
                    self.reg_entries['location'].get()
                )
            )
            self.db.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login_screen()
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry
                messagebox.showerror("Error", "Username already exists")
            else:
                messagebox.showerror("Database Error", f"Error during registration: {err}")

    def show_customer_dashboard(self):
        """Display beautifully styled customer dashboard"""
        self.clear_window()
        
        # Configure main window background
        self.root.configure(bg=self.colors["bg"])
        
        # Header frame with accent color
        header_frame = ttk.Frame(self.root, 
                                style="Card.TFrame",
                                padding=(20, 10))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Welcome message with user info
        welcome_label = ttk.Label(
            header_frame,
            text=f"Welcome back, {self.current_user['name']}",
            font=('Helvetica', 16, 'bold'),
            foreground=self.colors["primary"],
            background=self.colors["card"]
        )
        welcome_label.pack(side=tk.LEFT, padx=10)
        
        # Elegant logout button
        logout_btn = ttk.Button(
            header_frame,
            text="Logout",
            style="Pink.TButton",
            command=self.logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=10)
        
        # Main content area with subtle shadow
        content_frame = ttk.Frame(self.root, 
                                style="Card.TFrame",
                                padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Stylish notebook (tabs) with custom style
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["bg"])
        style.configure("TNotebook.Tab", 
                    font=('Helvetica', 11, 'bold'),
                    padding=(15, 5),
                    foreground=self.colors["primary"])
        
        style.map("TNotebook.Tab",
                background=[("selected", self.colors["card"])],
                expand=[("selected", (1, 1, 1, 0))])
        
        tab_control = ttk.Notebook(content_frame, style="TNotebook")
        
        # My Appointments Tab
        appointments_tab = ttk.Frame(tab_control, 
                                style="Card.TFrame",
                                padding=15)
        self.setup_customer_appointments_tab(appointments_tab)
        tab_control.add(appointments_tab, text="My Appointments")
        
        # Services Tab
        services_tab = ttk.Frame(tab_control, 
                                style="Card.TFrame",
                                padding=15)
        self.setup_services_tab(services_tab)
        tab_control.add(services_tab, text="Services & Booking")
        
        tab_control.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Add status bar at bottom
        status_frame = ttk.Frame(self.root, 
                                style="Card.TFrame",
                                height=25,
                                padding=(10, 5))
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Label(status_frame,
                text=f"Logged in as: {self.current_user['username']} | Customer Dashboard",
                style="Pink.TLabel",
                font=('Helvetica', 8)).pack(side=tk.LEFT)
        
    def setup_customer_appointments_tab(self, parent):
        """Setup customer appointments tab with refresh button"""
        # Create a container frame for header and button
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Title label on the left
        ttk.Label(header_frame, 
                text="My Appointments", 
                font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Refresh button on the right
        refresh_btn = ttk.Button(header_frame, 
                            text="Refresh", 
                            command=self.load_customer_appointments)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Table for appointments
        columns = ("ID", "Service", "Provider", "Date", "Start Time", "End Time", "Status")
        self.customer_appointments_tree = ttk.Treeview(parent, 
                                                    columns=columns, 
                                                    show="headings", 
                                                    height=10)

        # Configure columns
        for col in columns:
            self.customer_appointments_tree.heading(col, text=col)
            self.customer_appointments_tree.column(col, width=100, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.customer_appointments_tree.yview)
        self.customer_appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.customer_appointments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Load initial data
        self.load_customer_appointments()
        
    def load_customer_appointments(self):
        """Refresh customer appointments with proper query"""
        if not hasattr(self, 'customer_appointments_tree'):
            return
        
        for row in self.customer_appointments_tree.get_children():
            self.customer_appointments_tree.delete(row)

        try:
            self.cursor.execute("""
                SELECT a.id, s.service_name, u.name, a.appointment_date, 
                    a.start_time, a.end_time, a.status
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN users u ON a.provider_id = u.id
                WHERE a.customer_id = %s
                ORDER BY a.appointment_date, a.start_time
            """, (self.current_user['id'],))
            
            for appt in self.cursor.fetchall():
                self.customer_appointments_tree.insert("", "end", values=appt)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load appointments: {err}")



    def setup_services_tab(self, parent):
        """Improved services tab with booking functionality showing provider username"""
        ttk.Label(parent, text="Browse Services", font=('Arial', 12, 'bold')).pack(pady=10)

        # Filters frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Location:").pack(side=tk.LEFT, padx=5)
        self.location_var = tk.StringVar()
        location_dropdown = ttk.Combobox(filter_frame, textvariable=self.location_var)
        location_dropdown['values'] = self.get_unique_provider_locations()
        location_dropdown.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Service Type:").pack(side=tk.LEFT, padx=5)
        self.service_var = tk.StringVar()
        service_dropdown = ttk.Combobox(filter_frame, textvariable=self.service_var)
        service_dropdown['values'] = self.get_unique_service_types()
        service_dropdown.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Filter", command=self.filter_services).pack(side=tk.LEFT, padx=5)
        
        # Services treeview with provider username instead of description
        columns = ("ID", "Service", "Provider", "Price", "Duration", "Location")
        self.services_tree = ttk.Treeview(
            parent, 
            columns=columns, 
            show="headings",
            height=10,
            selectmode="browse"
        )
        
        # Configure columns
        col_widths = [50, 150, 150, 80, 80, 100]  # Adjust as needed
        for col, width in zip(columns, col_widths):
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=width, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Booking frame
        booking_frame = ttk.Frame(parent)
        booking_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(booking_frame, text="Select Date:").pack(side=tk.LEFT, padx=5)
        self.calendar = Calendar(booking_frame)
        self.calendar.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(booking_frame, text="Time (HH:MM):").pack(side=tk.LEFT, padx=5)
        self.time_var = tk.StringVar()
        time_entry = ttk.Entry(booking_frame, textvariable=self.time_var)
        time_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(booking_frame, 
                text="Book Appointment", 
                command=self.book_appointment).pack(side=tk.LEFT, padx=5)
        
        # Load initial services
        self.load_services()

    def get_unique_provider_locations(self):
        """Fetch unique provider locations from the database"""
        self.cursor.execute("SELECT DISTINCT location FROM users WHERE user_type = 'provider'")
        return [loc[0] for loc in self.cursor.fetchall()]
        
    def get_unique_service_types(self):
        """Fetch unique service types from the database"""
        self.cursor.execute("SELECT DISTINCT service_name FROM services")
        return [st[0] for st in self.cursor.fetchall()]

    def filter_services(self):
        """Fetch and display filtered services with provider username"""
        location = self.location_var.get()
        service_type = self.service_var.get()

        query = """
            SELECT s.id, s.service_name, u.username, s.price, s.duration, u.location
            FROM services s
            JOIN users u ON s.provider_id = u.id
            WHERE 1=1
        """
        params = []

        if location:
            query += " AND u.location = %s"
            params.append(location)

        if service_type:
            query += " AND s.service_name = %s"
            params.append(service_type)

        self.cursor.execute(query, params)
        self.update_services_tree(self.cursor.fetchall())

    def load_services(self):
        """Load all services with provider username"""
        self.cursor.execute("""
            SELECT s.id, s.service_name, u.username, s.price, s.duration, u.location
            FROM services s
            JOIN users u ON s.provider_id = u.id
        """)
        self.update_services_tree(self.cursor.fetchall())

    def update_services_tree(self, services):
        """Update the treeview with services data"""
        self.services_tree.delete(*self.services_tree.get_children())
        for service in services:
            self.services_tree.insert("", "end", values=service)
            
    def book_appointment(self):
        """Handle appointment booking with full validation and database integration"""
        # 1. Validate service selection
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a service")
            return
        
        # 2. Get selected service details
        service_values = self.services_tree.item(selected, "values")
        service_id = service_values[0]
        date_str = self.calendar.get_date()  # Get date as string from calendar
        time_str = self.time_var.get()

        # 3. Validate time format
        try:
            # Parse time separately first
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Please enter time in HH:MM format (e.g., 14:30)")
            return

        try:
            # 4. Parse the date from calendar (handles different date formats)
            try:
                # Try parsing with month-first format (common in US)
                date_obj = datetime.strptime(date_str, "%m/%d/%y").date()
            except ValueError:
                try:
                    # Try parsing with day-first format (common in other countries)
                    date_obj = datetime.strptime(date_str, "%d/%m/%y").date()
                except ValueError:
                    messagebox.showerror("Error", f"Invalid date format: {date_str}. Please use MM/DD/YY or DD/MM/YY")
                    return

            # 5. Get service duration and provider ID
            self.cursor.execute(
                "SELECT duration, provider_id FROM services WHERE id = %s",
                (service_id,)
            )
            service_data = self.cursor.fetchone()
            if not service_data:
                messagebox.showerror("Error", "Selected service not found")
                return

            duration, provider_id = service_data

            # 6. Combine date and time
            start_datetime = datetime.combine(date_obj, datetime.strptime(time_str, "%H:%M").time())
            end_datetime = start_datetime + timedelta(minutes=duration)
            start_time = start_datetime.time()
            end_time = end_datetime.time()

            # 7. Check for time slot availability
            self.cursor.execute(
                """
                SELECT id FROM appointments 
                WHERE provider_id = %s 
                AND appointment_date = %s 
                AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                )
                """,
                (
                    provider_id, 
                    date_obj,  # Use date_obj instead of date
                    start_time, 
                    start_time,
                    end_time, 
                    end_time,
                    start_time, 
                    end_time
                )
            )
            if self.cursor.fetchone():
                messagebox.showerror("Error", "Time slot not available. Please choose another time.")
                return

            # 8. Insert the appointment
            self.cursor.execute(
                """
                INSERT INTO appointments 
                (customer_id, service_id, provider_id, appointment_date, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                """,
                (
                    self.current_user['id'],
                    service_id,
                    provider_id,
                    date_obj,  # Use date_obj instead of date
                    start_time.strftime("%H:%M:%S"),
                    end_time.strftime("%H:%M:%S")
                )
            )
            self.db.commit()

            # Debug output
            print("Appointment booked successfully!")
            print(f"Customer ID: {self.current_user['id']}")
            print(f"Service ID: {service_id}")
            
            # Force immediate refresh
            self.refresh_all_views()
            
            messagebox.showinfo("Success", "Appointment booked successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to book appointment: {str(e)}")
            print("Error:", str(e))

    def refresh_all_views(self):
        """Refresh all relevant views"""
        # Refresh customer view
        if hasattr(self, 'load_customer_appointments'):
            try:
                self.load_customer_appointments()
                print("DEBUG: Refreshed customer appointments")
            except Exception as e:
                print(f"Error refreshing customer view: {str(e)}")
    
        # Refresh provider view
        if hasattr(self, 'load_provider_appointments'):
            try:
                self.load_provider_appointments()
                print("DEBUG: Refreshed provider appointments")
            except Exception as e:
                print(f"Error refreshing provider view: {str(e)}")
        
        # Force UI update
        self.root.update_idletasks()
        
    def show_provider_dashboard(self):
        """Display service provider dashboard"""
        self.clear_window()
        
        # Main frames
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        ttk.Label(header_frame, 
                 text=f"Welcome, {self.current_user['name']} (Service Provider)",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT)
        
        # Navigation tabs
        tab_control = ttk.Notebook(content_frame)
        
        # Appointments Tab
        appointments_tab = ttk.Frame(tab_control)
        self.setup_provider_appointments_tab(appointments_tab)
        tab_control.add(appointments_tab, text="Appointments")
        
        # Services Management Tab
        services_tab = ttk.Frame(tab_control)
        self.setup_provider_services_tab(services_tab)
        tab_control.add(services_tab, text="My Services")
        
        # Analytics Tab
        analytics_tab = ttk.Frame(tab_control)
        self.setup_analytics_tab(analytics_tab)
        tab_control.add(analytics_tab, text="Analytics")
        
        tab_control.pack(expand=1, fill="both")

    def setup_provider_appointments_tab(self, parent):
        """Setup provider appointments tab"""
        ttk.Label(parent, text="Your Appointments", font=('Arial', 12, 'bold')).pack(pady=10)

        # Table for appointments
        columns = ("ID", "Customer", "Service", "Date", "Start Time", "End Time", "Status", "Actions")
        self.appointments_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=100, anchor="center")

        self.appointments_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Action Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Confirm", command=lambda: self.change_status("confirmed")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Complete", command=lambda: self.change_status("completed")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.change_status("cancelled")).pack(side=tk.LEFT, padx=5)


        ttk.Button(parent, text="Refresh", command=self.load_provider_appointments).pack(pady=5)

        # Load appointments initially
    def load_provider_appointments(self):
        """Refresh provider appointments with proper query"""
        for row in self.appointments_tree.get_children():
            self.appointments_tree.delete(row)

        try:
            self.cursor.execute("""
                SELECT a.id, c.name, s.service_name, a.appointment_date,
                    a.start_time, a.end_time, a.status
                FROM appointments a
                JOIN users c ON a.customer_id = c.id
                JOIN services s ON a.service_id = s.id
                WHERE a.provider_id = %s
                ORDER BY a.appointment_date, a.start_time
            """, (self.current_user['id'],))
            
            for appt in self.cursor.fetchall():
                self.appointments_tree.insert("", "end", values=appt)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load appointments: {err}")

   
    def change_status(self, new_status):
        """Change the status of the selected appointment"""
        selected_item = self.appointments_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an appointment.")
            return

        appointment_id = self.appointments_tree.item(selected_item, "values")[0]  # Get appointment ID
        self.update_appointment_status(appointment_id, new_status)

    def update_appointment_status(self, appointment_id, new_status):
        """Update the status of an appointment"""
        try:
            self.cursor.execute(
                "UPDATE appointments SET status = %s WHERE id = %s",
                (new_status, appointment_id)
            )
            self.db.commit()
            messagebox.showinfo("Success", f"Appointment status updated to {new_status}")
            self.load_provider_appointments()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating status: {err}")


    def setup_provider_services_tab(self, parent):
        """Setup provider services management tab"""
        ttk.Label(parent, text="Manage Your Services", font=('Arial', 12, 'bold')).pack(pady=10)

        # Table for services
        columns = ("ID", "Service_name", "Description", "Price", "Duration")
        self.services_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=150, anchor="center")

        self.services_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Add Service", command=self.add_service_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Service", command=self.edit_service_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Service", command=self.delete_service).pack(side=tk.LEFT, padx=5)

        ttk.Button(parent, text="Refresh", command=self.load_provider_services).pack(pady=5)

        # Load existing services
        self.load_provider_services()

    def load_provider_services(self):
        """Fetch and display services for the logged-in provider"""
        for row in self.services_tree.get_children():
            self.services_tree.delete(row)  # Clear existing data

        try:
            self.cursor.execute("""
                SELECT id, service_name, description, price, duration
                FROM services 
                WHERE provider_id = %s
            """, (self.current_user['id'],))

            services = self.cursor.fetchall()

            for service in services:
                self.services_tree.insert("", "end", values=service)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching services: {err}")

    def add_service_popup(self):
        """Show popup to add a new service"""
        popup = tk.Toplevel(self.root)
        popup.title("Add Service")
        popup.geometry("400x300")

        ttk.Label(popup, text="Service Name:").pack(pady=5)
        name_entry = ttk.Entry(popup)
        name_entry.pack(pady=5)

        ttk.Label(popup, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(popup)
        desc_entry.pack(pady=5)

        ttk.Label(popup, text="Price:").pack(pady=5)
        price_entry = ttk.Entry(popup)
        price_entry.pack(pady=5)

        ttk.Label(popup, text="Duration (mins):").pack(pady=5)
        duration_entry = ttk.Entry(popup)
        duration_entry.pack(pady=5)

        def save_service():
            """Save service to database and refresh list"""
            service_name = name_entry.get()
            description = desc_entry.get()
            price = price_entry.get()
            duration = duration_entry.get()
            

            if not service_name or not price or not duration:
                messagebox.showerror("Error", "Please fill all required fields")
                return

            try:
                self.cursor.execute(
                    "INSERT INTO services (service_name, description, price, duration, provider_id) VALUES (%s, %s, %s, %s, %s)",
                    (service_name, description, price, duration, self.current_user['id'])
                )
                self.db.commit()
                messagebox.showinfo("Success", "Service added successfully!")
                popup.destroy()
                self.load_provider_services()  # Refresh services list
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error adding service: {err}")

        ttk.Button(popup, text="Save", command=save_service).pack(pady=10)

    def edit_service_popup(self):
        """Show popup to edit a selected service"""
        selected_item = self.services_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a service to edit.")
            return

        service_values = self.services_tree.item(selected_item, "values")
        service_id = service_values[0]

        popup = tk.Toplevel(self.root)
        popup.title("Edit Service")
        popup.geometry("400x300")

        fields = [("Service_name", "service_name"), ("Description", "description"), ("Price", "price"), ("Duration (mins)", "duration")]
        entries = {}

        for i, (label, key) in enumerate(fields):
            ttk.Label(popup, text=label).grid(row=i, column=0, pady=5, sticky=tk.W)
            entry = ttk.Entry(popup)
            entry.grid(row=i, column=1, pady=5)
            entry.insert(0, service_values[i + 1])  # Fill with current values
            entries[key] = entry

        def update_service():
            """Update service in database"""
            try:
                self.cursor.execute("""
                    UPDATE services 
                    SET service_name=%s, description=%s, price=%s, duration=%s
                    WHERE id=%s
                """, (
                    entries["service_name"].get(),
                    entries["description"].get(),
                    float(entries["price"].get()),
                    int(entries["duration"].get()),
                    service_id
                ))
                self.db.commit()
                messagebox.showinfo("Success", "Service updated successfully!")
                popup.destroy()
                self.load_provider_services()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error updating service: {err}")

        ttk.Button(popup, text="Update", command=update_service).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_service(self):
        """Delete selected service"""
        selected_item = self.services_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a service to delete.")
            return

        service_id = self.services_tree.item(selected_item, "values")[0]

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this service?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Service deleted successfully!")
                self.load_provider_services()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting service: {err}")

    def setup_analytics_tab(self, parent):
        """Setup analytics tab"""
        # Implementation would go here
        pass

    def logout(self):
        """Log out current user"""
        self.current_user = None
        self.user_type = None
        self.show_login_screen()

    def __del__(self):
        """Clean up database connection when object is destroyed"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.cursor.close()
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SalonApp(root)
    root.mainloop()
