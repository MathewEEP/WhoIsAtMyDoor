import src.GUI.classes as c
import src.GUI.predict as p
import sys
import os

os.environ['QT_MAC_WANTS_LAYER'] = '1'

if __name__ == "__main__":
    app = c.QApplication(c.sys.argv)
    splash_pix = c.QPixmap("animation.gif")
    splash = c.SplashScreen("animation.gif", c.Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    screen = app.primaryScreen()
    size = screen.size()
    main_window = c.Main(x=(size.width() // 2) - (500 // 2), y=(size.height() // 2) - (500 // 2))
    splash.finish(main_window)
    c.time.sleep(0.01)
    main_window.show()
    c.sys.exit(app.exec_())
