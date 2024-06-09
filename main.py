import gi
gi.require_version("Gtk", "4.0")
gi.require_version("WebKit2", "5.0")
from urllib.parse import urlparse, urlencode
from gi.repository import Gtk, WebKit2

class BrowserWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(800, 600)

        # Create a header bar with a title and a button to add tabs
        header = Gtk.HeaderBar()
        header.set_title("SimpleBrowse")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        add_button = Gtk.Button.new_from_icon_name("tab-new-symbolic")
        add_button.connect("clicked", self.on_add_tab_clicked)
        header.pack_end(add_button)

        # Create a notebook to hold the tabs
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(False)
        self.notebook.connect("page-removed", self.on_page_removed)
        self.set_child(self.notebook)

        # Add the first tab
        self.add_tab()

    def add_tab(self, url=None):
        # Create a web view to display the web page
        web_view = WebKit2.WebView()
        if url is None:
            # Load a default web page
            web_view.load_uri("https://www.qwant.com")
        else:
            url.replace("http://", "https://")
            url_define = urlparse(url)
            if url_define.netloc and url_define.scheme:
                web_view.load_uri(url)
            else:
                web_view.load_uri("https://www.qwant.com/?q=" + urlencode(url))

        label = Gtk.Label()
        web_view.connect("notify::title", self.on_title_changed, label)

        # Create a button to close the tab
        close_button = Gtk.Button.new_from_icon_name("window-close-symbolic")
        close_button.connect("clicked", self.on_close_tab_clicked, web_view)

        # Create a box to hold the label and the button
        box = Gtk.Box()
        box.set_spacing(4)
        box.append(label)
        box.append(close_button)

        # Add the tab to the notebook
        self.notebook.append_page(web_view, box)
        self.notebook.set_tab_reorderable(web_view, True)
        self.notebook.set_tab_detachable(web_view, True)
        self.notebook.show_child(web_view)

    def on_add_tab_clicked(self, button):
        # Ask the user for a url to load
        dialog = Gtk.Dialog.new()
        dialog.set_transient_for(self)
        dialog.set_modal(True)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Open", Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.set_activates_default(True)
        dialog.set_child(entry)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Get the url from the entry
            url = entry.get_text()
            # Add a new tab with the url
            self.add_tab(url)

        dialog.destroy()

    def on_close_tab_clicked(self, button, web_view):
        # Remove the tab from the notebook
        page_num = self.notebook.page_num(web_view)
        self.notebook.remove_page(page_num)

    def on_page_removed(self, notebook, child, page_num):
        # If there are no more tabs, close the window
        if notebook.get_n_pages() == 0:
            self.destroy()

    def on_title_changed(self, web_view, param, label):
        # Set the label text to the web page title
        label.set_text(web_view.get_title())

class BrowserApp(Gtk.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        win = BrowserWindow(self)
        win.present()

app = BrowserApp()
app.run()