"""
GUI Client for Cryptex secure chat application.
WhatsApp-style modern interface with chat bubbles.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, Frame
import threading
import config
from client import ChatClient
from utils import get_timestamp, validate_username, validate_ip, validate_port


class LoginWindow:
    """Login window for user authentication and server connection."""
    
    def __init__(self):
        """Initialize login window."""
        self.root = tk.Tk()
        self.root.title("Cryptex - Secure Login")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        self.root.configure(bg=config.WHATSAPP_DARK_BG)
        
        self.username = None
        self.host = None
        self.port = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create login form widgets."""
        # Title with WhatsApp-style header
        title_frame = tk.Frame(self.root, bg=config.ACCENT_COLOR, height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🔒 CRYPTEX",
            font=(config.FONT_FAMILY, 24, 'bold'),
            bg=config.ACCENT_COLOR,
            fg='white'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            title_frame,
            text="Secure End-to-End Encrypted Chat",
            font=(config.FONT_FAMILY, 11),
            bg=config.ACCENT_COLOR,
            fg='white'
        )
        subtitle_label.pack()
        
        # Form frame
        form_frame = tk.Frame(self.root, bg=config.WHATSAPP_DARK_BG)
        form_frame.pack(pady=30, padx=40, fill='both', expand=True)
        
        # Username
        tk.Label(
            form_frame,
            text="Username:",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_DARK_BG,
            fg=config.TEXT_COLOR
        ).grid(row=0, column=0, sticky='w', pady=8)
        
        self.username_entry = tk.Entry(
            form_frame,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_INPUT_BG,
            fg=config.TEXT_COLOR,
            insertbackground=config.TEXT_COLOR,
            relief='flat',
            bd=1
        )
        self.username_entry.grid(row=0, column=1, sticky='ew', pady=8, ipady=5)
        
        # Server Host
        tk.Label(
            form_frame,
            text="Server Host:",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_DARK_BG,
            fg=config.TEXT_COLOR
        ).grid(row=1, column=0, sticky='w', pady=8)
        
        self.host_entry = tk.Entry(
            form_frame,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_INPUT_BG,
            fg=config.TEXT_COLOR,
            insertbackground=config.TEXT_COLOR,
            relief='flat',
            bd=1
        )
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=1, column=1, sticky='ew', pady=8, ipady=5)
        
        # Server Port
        tk.Label(
            form_frame,
            text="Server Port:",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_DARK_BG,
            fg=config.TEXT_COLOR
        ).grid(row=2, column=0, sticky='w', pady=8)
        
        self.port_entry = tk.Entry(
            form_frame,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.WHATSAPP_INPUT_BG,
            fg=config.TEXT_COLOR,
            insertbackground=config.TEXT_COLOR,
            relief='flat',
            bd=1
        )
        self.port_entry.insert(0, str(config.DEFAULT_PORT))
        self.port_entry.grid(row=2, column=1, sticky='ew', pady=8, ipady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Connect button
        self.connect_btn = tk.Button(
            self.root,
            text="Connect",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, 'bold'),
            bg=config.BUTTON_COLOR,
            fg='white',
            activebackground=config.BUTTON_HOVER_COLOR,
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.validate_and_connect
        )
        self.connect_btn.pack(pady=15)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.validate_and_connect())
        
        # Focus on username
        self.username_entry.focus()
        
    def validate_and_connect(self):
        """Validate inputs and attempt connection."""
        username = self.username_entry.get().strip()
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        
        # Validate username
        valid, msg = validate_username(username)
        if not valid:
            messagebox.showerror("Invalid Username", msg)
            return
        
        # Validate host
        valid, msg = validate_ip(host)
        if not valid:
            messagebox.showerror("Invalid Host", msg)
            return
        
        # Validate port
        valid, msg = validate_port(port)
        if not valid:
            messagebox.showerror("Invalid Port", msg)
            return
        
        self.username = username
        self.host = host
        self.port = int(port)
        
        self.root.destroy()
    
    def show(self):
        """Show login window and return credentials."""
        self.root.mainloop()
        return self.username, self.host, self.port


class ChatBubble:
    """Represents a single chat bubble message."""
    
    def __init__(self, canvas, message, sender, is_sent, timestamp, y_position):
        """Create a chat bubble."""
        self.canvas = canvas
        self.message = message
        self.sender = sender
        self.is_sent = is_sent
        self.timestamp = timestamp
        self.y_position = y_position
        
        self.draw()
    
    def draw(self):
        """Draw the chat bubble on canvas."""
        # Configuration
        max_width = 400
        padding_x = 12
        padding_y = 8
        margin = 10
        timestamp_height = 18  # Space for timestamp
        sender_name_height = 18 if not self.is_sent else 0  # Space for sender name
        
        # Calculate text dimensions
        temp_text = self.canvas.create_text(
            0, 0,
            text=self.message,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            width=max_width - 2 * padding_x - 60  # Reserve space for timestamp on last line
        )
        bbox = self.canvas.bbox(temp_text)
        self.canvas.delete(temp_text)
        
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Bubble dimensions - properly account for all elements
        bubble_width = min(text_width + 2 * padding_x + 60, max_width)  # Extra width for timestamp
        bubble_height = text_height + 2 * padding_y + sender_name_height + timestamp_height
        
        # Calculate position
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 800  # Default width
        
        if self.is_sent:
            # Right-aligned for sent messages
            x = canvas_width - bubble_width - margin
            bg_color = config.BUBBLE_SENT_BG
        else:
            # Left-aligned for received messages
            x = margin
            bg_color = config.BUBBLE_RECEIVED_BG
        
        y = self.y_position
        
        # Draw rounded rectangle (bubble)
        radius = 8
        self.canvas.create_arc(x, y, x + radius * 2, y + radius * 2,
                              start=90, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x + bubble_width - radius * 2, y,
                              x + bubble_width, y + radius * 2,
                              start=0, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x, y + bubble_height - radius * 2,
                              x + radius * 2, y + bubble_height,
                              start=180, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(x + bubble_width - radius * 2,
                              y + bubble_height - radius * 2,
                              x + bubble_width, y + bubble_height,
                              start=270, extent=90, fill=bg_color, outline=bg_color)
        
        self.canvas.create_rectangle(x + radius, y, x + bubble_width - radius,
                                     y + bubble_height, fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(x, y + radius, x + bubble_width,
                                     y + bubble_height - radius, fill=bg_color, outline=bg_color)
        
        # Sender name for received messages
        content_y = y + padding_y
        if not self.is_sent:
            self.canvas.create_text(
                x + padding_x, content_y,
                text=self.sender,
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, 'bold'),
                fill=config.ACCENT_COLOR,
                anchor='nw'
            )
            content_y += sender_name_height
        
        # Message text
        self.canvas.create_text(
            x + padding_x, content_y,
            text=self.message,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            fill=config.TEXT_COLOR,
            anchor='nw',
            width=max_width - 2 * padding_x - 60
        )
        
        # Timestamp (bottom right of bubble, on its own line)
        self.canvas.create_text(
            x + bubble_width - padding_x, y + bubble_height - padding_y - 3,
            text=self.timestamp,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL - 1),
            fill=config.TIMESTAMP_COLOR,
            anchor='se'
        )
        
        # Return the total height used
        return bubble_height + 8  # 8px spacing between bubbles


class ChatWindow:
    """Main chat window with WhatsApp-style design."""
    
    def __init__(self, client):
        """Initialize chat window."""
        self.client = client
        self.root = tk.Tk()
        self.root.title(f"Cryptex - {client.username}")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.MAIN_BG_COLOR)
        
        # Set up client callbacks
        self.client.on_message_received = self.on_message_received
        self.client.on_user_list_update = self.on_user_list_update
        self.client.on_connection_status = self.on_connection_status
        self.client.on_error = self.on_error
        
        self.online_users = []
        self.selected_recipient = 'ALL'
        self.current_y = 10  # Track Y position for bubbles
        self.messages = []  # Store all messages for redrawing
        self.resize_timer = None  # Timer for resize debouncing
        
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """Create chat interface widgets."""
        # Top bar - WhatsApp style
        top_bar = tk.Frame(self.root, bg=config.WHATSAPP_HEADER, height=60)
        top_bar.pack(fill='x', side='top')
        top_bar.pack_propagate(False)
        
        # Left side of top bar
        left_top = tk.Frame(top_bar, bg=config.WHATSAPP_HEADER)
        left_top.pack(side='left', padx=15, pady=10)
        
        title_label = tk.Label(
            left_top,
            text=f"CRYPTEX",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, 'bold'),
            bg=config.WHATSAPP_HEADER,
            fg=config.TEXT_COLOR
        )
        title_label.pack(side='left')
        
        # Right side of top bar - status
        self.status_label = tk.Label(
            top_bar,
            text="● Connecting...",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            bg=config.WHATSAPP_HEADER,
            fg='#FFB74D'
        )
        self.status_label.pack(side='right', padx=20, pady=10)
        
        # Main container
        main_container = tk.Frame(self.root, bg=config.MAIN_BG_COLOR)
        main_container.pack(fill='both', expand=True)
        
        # Left sidebar - User list
        sidebar = tk.Frame(main_container, bg=config.SIDEBAR_BG_COLOR, width=250)
        sidebar.pack(fill='y', side='left')
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(sidebar, bg=config.SIDEBAR_BG_COLOR)
        sidebar_header.pack(fill='x', pady=15, padx=15)
        
        sidebar_title = tk.Label(
            sidebar_header,
            text="Chats",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, 'bold'),
            bg=config.SIDEBAR_BG_COLOR,
            fg=config.TEXT_COLOR
        )
        sidebar_title.pack(anchor='w')
        
        # User label
        user_label = tk.Label(
            sidebar_header,
            text=f"Logged in as: {self.client.username}",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            bg=config.SIDEBAR_BG_COLOR,
            fg=config.TIMESTAMP_COLOR
        )
        user_label.pack(anchor='w', pady=(5, 0))
        
        # Separator line
        separator = tk.Frame(sidebar, bg=config.WHATSAPP_BORDER, height=1)
        separator.pack(fill='x')
        
        # Scrollable user list with canvas for custom chat items
        user_list_container = tk.Frame(sidebar, bg=config.SIDEBAR_BG_COLOR)
        user_list_container.pack(fill='both', expand=True)
        
        user_canvas = Canvas(user_list_container, bg=config.SIDEBAR_BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(user_list_container, orient='vertical', command=user_canvas.yview)
        self.user_list_frame = tk.Frame(user_canvas, bg=config.SIDEBAR_BG_COLOR)
        
        self.user_list_frame.bind(
            '<Configure>',
            lambda e: user_canvas.configure(scrollregion=user_canvas.bbox('all'))
        )
        
        user_canvas.create_window((0, 0), window=self.user_list_frame, anchor='nw')
        user_canvas.configure(yscrollcommand=scrollbar.set)
        
        user_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Dictionary to track chat item frames
        self.chat_items = {}
        
        # Add "Everyone" broadcast item
        self.add_chat_item("📢", "Everyone", "Broadcast to all users", is_broadcast=True)
        
        # Right side - Chat area
        chat_container = tk.Frame(main_container, bg=config.MAIN_BG_COLOR)
        chat_container.pack(fill='both', expand=True, side='right')
        
        # Chat header
        chat_header = tk.Frame(chat_container, bg=config.WHATSAPP_HEADER, height=60)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        # Recipient info
        recipient_frame = tk.Frame(chat_header, bg=config.WHATSAPP_HEADER)
        recipient_frame.pack(side='left', padx=20, pady=10)
        
        self.recipient_label = tk.Label(
            recipient_frame,
            text="Everyone",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE - 1, 'bold'),
            bg=config.WHATSAPP_HEADER,
            fg=config.TEXT_COLOR
        )
        self.recipient_label.pack(anchor='w')
        
        self.recipient_status = tk.Label(
            recipient_frame,
            text="Broadcast to all users",
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            bg=config.WHATSAPP_HEADER,
            fg=config.TIMESTAMP_COLOR
        )
        self.recipient_status.pack(anchor='w')
        
        # Chat header separator
        chat_header_sep = tk.Frame(chat_container, bg=config.WHATSAPP_BORDER, height=1)
        chat_header_sep.pack(fill='x')
        
        # Message display area with Canvas for bubbles
        message_container = tk.Frame(chat_container, bg=config.MESSAGE_AREA_BG)
        message_container.pack(fill='both', expand=True)
        
        # Scrollbar for message area
        scrollbar = tk.Scrollbar(message_container)
        scrollbar.pack(side='right', fill='y')
        
        self.message_canvas = Canvas(
            message_container,
            bg=config.MESSAGE_AREA_BG,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.message_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.message_canvas.yview)
        
        # Bind canvas resize
        self.message_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Input area separator
        input_separator = tk.Frame(chat_container, bg=config.WHATSAPP_BORDER, height=1)
        input_separator.pack(fill='x')
        
        # Input area
        input_container = tk.Frame(chat_container, bg=config.WHATSAPP_DARK_BG)
        input_container.pack(fill='x', padx=15, pady=12)
        
        # Input field
        input_frame = tk.Frame(input_container, bg=config.INPUT_BG_COLOR, relief='solid', bd=1)
        input_frame.pack(fill='both', side='left', expand=True)
        
        self.message_input = tk.Text(
            input_frame,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.INPUT_BG_COLOR,
            fg=config.TEXT_COLOR,
            relief='flat',
            bd=0,
            height=2,
            wrap='word',
            insertbackground=config.TEXT_COLOR
        )
        self.message_input.pack(fill='both', padx=10, pady=8)
        
        # Send button
        self.send_btn = tk.Button(
            input_container,
            text="Send",
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, 'bold'),
            bg=config.BUTTON_COLOR,
            fg='black',
            activebackground=config.BUTTON_HOVER_COLOR,
            activeforeground='black',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.send_message
        )
        self.send_btn.pack(side='right', padx=(10, 0))
        
        # Bind Enter to send (Shift+Enter for new line)
        self.message_input.bind('<Return>', self.on_enter_press)
        
        # Display welcome message
        self.display_system_message("🔒 End-to-end encryption enabled. Your messages are secure.")
    
    def add_chat_item(self, icon_or_initials, name, status="", is_broadcast=False):
        """Add a WhatsApp-style chat item to the list."""
        username = "ALL" if is_broadcast else name
        
        # Create main frame for chat item
        item_frame = tk.Frame(self.user_list_frame, bg=config.SIDEBAR_BG_COLOR, cursor='hand2')
        item_frame.pack(fill='x', padx=5, pady=2)
        
       # Inner frame for padding and hover effect
        inner_frame = tk.Frame(item_frame, bg=config.SIDEBAR_BG_COLOR)
        inner_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Avatar circle (left side)
        avatar_frame = tk.Frame(inner_frame, bg=config.SIDEBAR_BG_COLOR)
        avatar_frame.pack(side='left', padx=(5, 10))
        
        # Canvas for circular avatar
        avatar_canvas = Canvas(avatar_frame, width=40, height=40, bg=config.SIDEBAR_BG_COLOR, highlightthickness=0)
        avatar_canvas.pack()
        
        # Draw circle
        if is_broadcast:
            circle_color = config.ACCENT_COLOR
        else:
            circle_color = '#2A3942'  # Dark gray for users
        
        avatar_canvas.create_oval(2, 2, 38, 38, fill=circle_color, outline=circle_color)
        
        # Add text/emoji in circle
        avatar_canvas.create_text(
            20, 20,
            text=icon_or_initials if len(icon_or_initials) <= 2 else icon_or_initials[:2].upper(),
            font=(config.FONT_FAMILY, 14 if len(icon_or_initials) > 1 else 16, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Text area (right side)
        text_frame = tk.Frame(inner_frame, bg=config.SIDEBAR_BG_COLOR)
        text_frame.pack(side='left', fill='both', expand=True)
        
        # User name
        name_label = tk.Label(
            text_frame,
           text=name,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, 'bold' if is_broadcast else 'normal'),
            bg=config.SIDEBAR_BG_COLOR,
            fg=config.TEXT_COLOR,
            anchor='w'
        )
        name_label.pack(fill='x')
        
        # Status/subtitle
        if status:
            status_label = tk.Label(
                text_frame,
                text=status,
                font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                bg=config.SIDEBAR_BG_COLOR,
                fg=config.TIMESTAMP_COLOR,
                anchor='w'
            )
            status_label.pack(fill='x')
        
        # Store reference
        self.chat_items[username] = {
            'frame': item_frame,
            'inner_frame': inner_frame,
            'name': name,
            'status': status
        }
        
        # Hover effects
        def on_enter(e):
            inner_frame.config(bg='#2A3942')
            avatar_frame.config(bg='#2A3942')
            text_frame.config(bg='#2A3942')
            name_label.config(bg='#2A3942')
            if status:
                status_label.config(bg='#2A3942')
        
        def on_leave(e):
            # Only reset if not selected
            if self.selected_recipient != username:
                inner_frame.config(bg=config.SIDEBAR_BG_COLOR)
                avatar_frame.config(bg=config.SIDEBAR_BG_COLOR)
                text_frame.config(bg=config.SIDEBAR_BG_COLOR)
                name_label.config(bg=config.SIDEBAR_BG_COLOR)
                if status:
                    status_label.config(bg=config.SIDEBAR_BG_COLOR)
        
        def on_click(e):
            self.select_chat_item(username, name)
        
        # Bind events to all components
        for widget in [item_frame, inner_frame, avatar_frame, avatar_canvas, text_frame, name_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
        if status:
            status_label.bind('<Enter>', on_enter)
            status_label.bind('<Leave>', on_leave)
            status_label.bind('<Button-1>', on_click)
    
    def select_chat_item(self, username, display_name):
        """Select a chat item and update UI."""
        # Clear previous selection
        for user, item_data in self.chat_items.items():
            if user == self.selected_recipient:
                inner_frame = item_data['inner_frame']
                # Reset background for all child widgets
                inner_frame.config(bg=config.SIDEBAR_BG_COLOR)
                for child in inner_frame.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.config(bg=config.SIDEBAR_BG_COLOR)
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Label):
                                subchild.config(bg=config.SIDEBAR_BG_COLOR)
        
        # Set new selection
        self.selected_recipient = username
        
        if username in self.chat_items:
            item_data = self.chat_items[username]
            inner_frame = item_data['inner_frame']
            # Highlight selected item
            inner_frame.config(bg='#2A3942')
            for child in inner_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg='#2A3942')
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(bg='#2A3942')
            
            # Update header
            self.recipient_label.config(text=display_name)
            if username == 'ALL':
                self.recipient_status.config(text="Broadcast to all users")
            else:
                self.recipient_status.config(text="Encrypted chat")
        
    def on_canvas_resize(self, event):
        """Handle canvas resize to redraw bubbles."""
        # Debounce resize events - only redraw after user stops resizing
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        
        self.resize_timer = self.root.after(200, self.redraw_messages)
    
    def on_enter_press(self, event):
        """Handle Enter key press in message input."""
        # Shift+Enter = new line, Enter = send
        if not event.state & 0x1:  # Check if Shift is not pressed
            self.send_message()
            return 'break'  # Prevent default newline
        return None
    
    def send_message(self):
        """Send message to selected recipient."""
        message = self.message_input.get('1.0', 'end-1c').strip()
        
        if not message:
            return
        
        if not self.client.connected:
            messagebox.showwarning("Not Connected", "You are not connected to the server.")
            return
        
        # Send message
        success = self.client.send_message(self.selected_recipient, message)
        
        if success:
            # Display sent message as bubble
            timestamp = get_timestamp()
            self.add_message_bubble(message, "You", True, timestamp)
            
            # Clear input
            self.message_input.delete('1.0', tk.END)
        else:
            messagebox.showerror("Send Failed", "Failed to send message.")
    
    def add_message_bubble(self, message, sender, is_sent, timestamp):
        """Add a message bubble to the canvas."""
        # Store message data for redrawing on resize
        self.messages.append({
            'type': 'bubble',
            'message': message,
            'sender': sender,
            'is_sent': is_sent,
            'timestamp': timestamp
        })
        
        bubble = ChatBubble(
            self.message_canvas,
            message,
            sender,
            is_sent,
            timestamp,
            self.current_y
        )
        
        # Update Y position
        height = bubble.draw()
        if height:
            self.current_y += height
        else:
            self.current_y += 80
        
        # Update scroll region
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox('all'))
        self.message_canvas.yview_moveto(1.0)
    
    def redraw_messages(self):
        """Redraw all messages on canvas resize."""
        # Clear canvas
        self.message_canvas.delete('all')
        
        # Reset Y position
        self.current_y = 10
        
        # Redraw all messages
        for msg_data in self.messages:
            if msg_data['type'] == 'bubble':
                bubble = ChatBubble(
                    self.message_canvas,
                    msg_data['message'],
                    msg_data['sender'],
                    msg_data['is_sent'],
                    msg_data['timestamp'],
                    self.current_y
                )
                height = bubble.draw()
                if height:
                    self.current_y += height
                else:
                    self.current_y += 80
            elif msg_data['type'] == 'system':
                self._draw_system_message(msg_data['message'])
        
        # Update scroll region
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox('all'))
        self.message_canvas.yview_moveto(1.0)
    
    def display_system_message(self, message):
        """Display system message (centered)."""
        # Store for redrawing
        self.messages.append({
            'type': 'system',
            'message': message
        })
        
        self._draw_system_message(message)
    
    def _draw_system_message(self, message):
        """Helper method to draw system message on canvas."""
        canvas_width = self.message_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 800
        
        # Calculate dimensions
        padding = 10
        temp_text = self.message_canvas.create_text(
            0, 0,
            text=message,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL)
        )
        bbox = self.message_canvas.bbox(temp_text)
        self.message_canvas.delete(temp_text)
        
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        box_width = text_width + 2 * padding
        box_height = text_height + 2 * padding
        
        x = (canvas_width - box_width) / 2
        y = self.current_y
        
        # Draw rounded box
        radius = 5
        bg_color = config.SYSTEM_MSG_BG
        
        self.message_canvas.create_rectangle(
            x + radius, y,
            x + box_width - radius, y + box_height,
            fill=bg_color, outline=bg_color
        )
        self.message_canvas.create_rectangle(
            x, y + radius,
            x + box_width, y + box_height - radius,
            fill=bg_color, outline=bg_color
        )
        
        # Add arcs for corners
        for corner_x, corner_y, start in [
            (x, y, 90),
            (x + box_width - 2*radius, y, 0),
            (x, y + box_height - 2*radius, 180),
            (x + box_width - 2*radius, y + box_height - 2*radius, 270)
        ]:
            self.message_canvas.create_arc(
                corner_x, corner_y,
                corner_x + 2*radius, corner_y + 2*radius,
                start=start, extent=90, fill=bg_color, outline=bg_color
            )
        
        # Add text
        self.message_canvas.create_text(
            x + box_width/2, y + box_height/2,
            text=message,
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            fill=config.SYSTEM_MSG_TEXT,
            anchor='center'
        )
        
        self.current_y += box_height + 12
        
        # Update scroll region
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox('all'))
        self.message_canvas.yview_moveto(1.0)
    
    def on_message_received(self, sender, message):
        """Callback for received messages."""
        def display():
            timestamp = get_timestamp()
            self.add_message_bubble(message, sender, False, timestamp)
        
        self.root.after(0, display)
    
    def on_user_list_update(self, users):
        """Callback for user list updates."""
        def update():
            self.online_users = [u for u in users if u != self.client.username]
            
            # Remove all user items except broadcast
            users_to_remove = [u for u in self.chat_items.keys() if u != 'ALL']
            for username in users_to_remove:
                if username in self.chat_items:
                    self.chat_items[username]['frame'].destroy()
                    del self.chat_items[username]
            
            # Add current online users
            for user in self.online_users:
                initials = user[:2].upper() if len(user) >= 2 else user[0].upper()
                self.add_chat_item(initials, user, "online", is_broadcast=False)
            
            # Display system message
            if len(self.online_users) > 0:
                user_list = ', '.join(self.online_users)
                self.display_system_message(f"Online: {user_list}")
        
        self.root.after(0, update)
    
    def on_connection_status(self, connected, message):
        """Callback for connection status changes."""
        def update():
            if connected:
                self.status_label.config(text="● Connected", fg='#90EE90')
            else:
                self.status_label.config(text="● Disconnected", fg='#FFB6C1')
                self.display_system_message(f"Connection status: {message}")
        
        self.root.after(0, update)
    
    def on_error(self, error_message):
        """Callback for errors."""
        self.root.after(0, lambda: messagebox.showerror("Error", error_message))
    
    def on_closing(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit Cryptex?"):
            self.client.disconnect()
            self.root.destroy()
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point for GUI client."""
    # Show login window
    login = LoginWindow()
    username, host, port = login.show()
    
    if not username:
        print("Login cancelled")
        return
    
    # Create client
    client = ChatClient(username, host, port)
    
    # Connect in background thread
    def connect():
        success = client.connect()
        if not success:
            # Connection failed is already handled by callbacks
            pass
    
    connect_thread = threading.Thread(target=connect, daemon=True)
    connect_thread.start()
    
    # Show chat window
    chat_window = ChatWindow(client)
    chat_window.run()


if __name__ == "__main__":
    main()
