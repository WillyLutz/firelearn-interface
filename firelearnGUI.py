from scripts import main

if __name__ == '__main__':
    main.main()

# to generate the distribution for linux, with the venv activated
# >>> pyinstaller firelearnGUI.spec
# >>> y

# to run the distribution
# >>> cd ../dist/firelearnGUI
# >>> ./firelearnGUI

# to generate the distribution for windows,
# pyinstaller --noconfirm --onedir firelearnGUI.py --add-data "C:\Users\wlutz\PycharmProjects\firelearn-interface\venv\Lib\site-packages\customtkinter:." --add-data "C:\Users\wlutz\PycharmProjects\firelearn-interface\data:data"
