 #!/usr/bin/env python

import wx
import hpiview_window
import hpiview_callbacks


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = hpiview_window.Hpiview_Window(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
