import e32
import appuifw
import key_codes
import time

class selectbox:
    def __init__(self,list,my_itemslist):
      self.g_time = 0
      self.my_timer = e32.Ao_timer()
      self.g_t = None
      self.my_list = list
 
      self.lb3 = None       # Listbox
      self.e3 = []          # Entries: list items with icons
      self.my_items = my_itemslist    # Save selections for next time
      self.icon_on = None   # Icon for selected checkbox
      self.icon_off = None  # Icon for non-selected checkbox
      
    def get_checkbox(self,a_value):
        ''' Checkbox icon: selected or not '''
        # Create only once, reuse after that
        if not self.icon_on:
            # See avkon2.mbm content (old version)
            # http://alindh.iki.fi/symbian/avkon2.mbm/
     
            try:
                # webkit checkbox looks better, but might not exist
                self.icon_off = appuifw.Icon(u"z:\\resource\\apps\\webkit.mbm", 12, 31)
                self.icon_on = appuifw.Icon(u"z:\\resource\\apps\\webkit.mbm", 13, 32)
            except:
                # Counting on avkon2 to be there, hopefully with checkbox
                self.icon_off = appuifw.Icon(u"z:\\resource\\apps\\avkon2.mbm", 103, 104)
                self.icon_on = appuifw.Icon(u"z:\\resource\\apps\\avkon2.mbm", 109, 110)
     
        if a_value:
            return self.icon_on
        else:
            return self.icon_off
     
    def cb_select(self):
        self.my_timer.cancel()
        # Ignore first and non-timer trickered events
        if (not self.g_time) or (time.clock() - self.g_time < 0.1):
            self.g_time = time.clock()
            # Should be more than start keyrepeat rate
            self.my_timer.after(0.15, self.cb_select)
            return
        self.g_time = 0
        ### keypress handler trick, done
     
        # Current listbox selection
        index = self.lb3.current()
     
        # Change selected item icon: on <-> off
        if self.e3[index][1] == self.icon_on:
            new_icon = self.icon_off
        else:
            new_icon = self.icon_on
     
        self.e3[index] = (self.e3[index][0], new_icon)
     
        # Show new list, same item selected
        self.lb3.set_list(self.e3, index)
        appuifw.app.body = self.lb3
     
        # Make it visible
        e32.ao_yield()
     
    def cb_return(self):
        self.my_items = tuple(i for i,x in enumerate(self.e3) if x[1] == self.icon_on)
        return self.my_items
    
    
    def menu_list3(self):
        self.e3 = []
     
        # Mark initial selections
        for item in range(len(self.my_list)):
            if item in self.my_items:
                icon = self.get_checkbox(item in self.my_items)
            else:
                icon = self.get_checkbox(False)
            self.e3.append((self.my_list[item], icon))
     
        self.lb3 = appuifw.Listbox(self.e3, self.cb_select)
        appuifw.app.body = self.lb3
        
     
        # Several ways to select item
        # BUG: One press of Enter/Select gives two events: KeyDown and KeyUp
        # BUG: ...or even 3+ with key repeat
        # Fix: write own key handler, react only on KeyUp event
        # Fix: use timer to separate "one" key press
        self.lb3.bind(key_codes.EKeyRightArrow, self.cb_select)
        self.lb3.bind(key_codes.EKeyEnter, self.cb_select)
        self.lb3.bind(key_codes.EKeySelect, self.cb_select) 
        
        