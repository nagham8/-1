import os
import importlib.util

# Определяем путь к файлу menu.py
menu_path = os.path.join(os.path.dirname(__file__), "ui", "menu.py")

spec = importlib.util.spec_from_file_location("menu", menu_path)
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)

if __name__ == "__main__":
    menu.run_menu()
