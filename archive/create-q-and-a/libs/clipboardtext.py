import win32clipboard

def getClipboardData():
    # get clipboard data
    win32clipboard.OpenClipboard()
    if win32clipboard.IsClipboardFormatAvailable(1):
        data = win32clipboard.GetClipboardData()
        return data
    else:
        return None
    win32clipboard.CloseClipboard()