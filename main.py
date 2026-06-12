import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from UI.app import BancoApp

if __name__ == "__main__":
    app = BancoApp()
    app.mainloop()