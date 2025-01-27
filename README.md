/home/luiz/.asdf/installs/python/3.10.0/bin/pyinstaller --onefile --hidden-import=requests
--hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtCore --hidden-import=systemd.journal
main.py && cp ./dist/main /opt/retropie/configs/all/autostart
