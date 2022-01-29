from collections import namedtuple
from webbrowser import WindowsDefault
import numpy
import random
import os
import sys
import pyautogui
import PIL
import keyboard
import time
import win32gui, win32con


# TODO: refactor into multiple scripts
# TODO: make scalable to any window size so that maximization is not necessary
# TODO: gold constraints?
# TODO: alternative stop condition on bookmarks purchased?


######################################################
# 
#               C O N S T A N T S
#
######################################################
SSHOP_SKYSTONE_COST = 3
DELAY_LOWER_BOUND = 0.2
DELAY_UPPER_BOUND = 0.7
CLICK_COUNTS = [i for i in range(2, 4)]

REFRESH_PNG = 'assets/refresh.png'
CONFIRM_PNG = 'assets/confirm.png'
BLUE_BOOKMARK_PNG = 'assets/covenant_bookmark.png'
MYSTIC_BOOKMARK_PNG = 'assets/mystic_bookmark.png'
BUY_PNG = 'assets/buy.png'

    # 1. Set duration of buying
    # 2. Detect bluestacks window
    # 3. Scan for bookmarks -> buy any on screen
    # exit if f3 is pressed

Button = namedtuple('Button', 'left top width height')
repeat = True

######################################################
# 
#                 H E L P E R S
#
######################################################

def delay():
    time.sleep(random.uniform(DELAY_LOWER_BOUND, DELAY_UPPER_BOUND))

def getGaussianXY(button):
    '''
    This function returns the XY coordinates of a button press of a two-tuple following a Normal distribution bounded by the button area.

    @param button   The button handle. 
                    ASSUMES a four-tuple (left, top, width, height) returned by a call to pyautogui.locateOnScreen().
    '''
    # the multiply by 2 is a math trick; (2*left) + width == left + (left + width)
    x = random.gauss((2 * button.left + button.width) / 2, button.width / 3)
    y = random.gauss((2 * button.top + button.height) / 2, button.height / 3)

    if x < button.left:
        x = button.left
    elif x > button.left + button.width:
        x = button.left + button.width

    if y < button.top:
        y = button.top
    elif y > button.top + button.height:
        y = button.top + button.height

    return x, y


def findBookmark(win_width, win_height):
    REFRESH_X = win_width * 0.06
    REFRESH_Y = win_height * 0.91
    REFRESH_WIDTH = win_width * 0.21
    REFRESH_HEIGHT = win_height * 0.04

    refreshButton = Button(REFRESH_X, REFRESH_Y, REFRESH_WIDTH, REFRESH_HEIGHT)
    x, y = getGaussianXY(refreshButton)
    delay()

    pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(0.2, 0.4))
    delay()

    CONFIRM_X = win_width * 0.505
    CONFIRM_Y = win_height * 0.61
    CONFIRM_WIDTH = win_width * 0.132
    CONFIRM_HEIGHT = win_height * 0.055

    confirmButton = Button(CONFIRM_X, CONFIRM_Y, CONFIRM_WIDTH, CONFIRM_HEIGHT)
    x, y = getGaussianXY(confirmButton)

    pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(0.2, 0.4))
    delay()



def buyBookmark(bookmark, win_width, win_height):
    '''
    @param  bookmark
            A tuple of the bookmark icon XY coordinates
    '''
    if bookmark:
        BOOKMARK_OFFSET_X = win_width / 2.77
        BOOKMARK_OFFSET_Y = win_height / 100
        BOOKMARK_BUTTON_WIDTH = win_width / 8
        BOOKMARK_BUTTON_HEIGHT = win_height / 20

        bookmark_button = Button(bookmark.x + BOOKMARK_OFFSET_X, bookmark.y + BOOKMARK_OFFSET_Y,
                                          bookmark.x + BOOKMARK_OFFSET_X + BOOKMARK_BUTTON_WIDTH,
                                          bookmark.y + BOOKMARK_OFFSET_Y + BOOKMARK_BUTTON_HEIGHT)

        x, y = getGaussianXY(bookmark_button)

        pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(0.2, 0.4))
        delay()

        BUY_X = win_width * 0.50
        BUY_Y = win_height * 0.6
        BUY_WIDTH = win_width * 0.14
        BUY_HEIGHT = win_height * 0.07

        buy_button = Button(BUY_X, BUY_Y, BUY_WIDTH, BUY_HEIGHT)
        x, y = getGaussianXY(buy_button)

        pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(0.2, 0.4))
        delay()





######################################################
# 
#                     M A I N
#
######################################################


def main():

    WIDTH, HEIGHT = pyautogui.size()


    print(''' 
##################################################################
# 
#   Welcome to the Epic Seven Secret Shop Bookmark Buyer (ESSB)!
#
##################################################################

Ensure that you are in the Secret Shop interface of the game.

If the tool fails to work, try:
- Manually taking screenshots of the shop bookmarks similar to the existing ones in /assets
- Editing the global constants in buyer.py.

Once the tool starts, you may press Ctrl + C to force abort.
    ''')

    skystones_to_spend = int(input('How many skystones would you like to spend on the Secret Shop?\n>> '))
    if skystones_to_spend < SSHOP_SKYSTONE_COST:
        input('Insufficient skystones. Press enter to exit . . .')
        sys.exit()

    window = win32gui.FindWindow(None, 'BlueStacks')

    if not window:
        print("ERROR: BlueStacks window not found.")
        input('Press Enter to exit . . .')
        sys.exit()    

    print("Found BlueStacks window.\n")

    # Maximize window
    win32gui.ShowWindow(window, win32con.SW_MAXIMIZE)

    # Set active window
    win32gui.SetForegroundWindow(window)

    time.sleep(0.1)

    blue_count, mystic_count = 0, 0

    for skystones in range(0, skystones_to_spend, SSHOP_SKYSTONE_COST):
        findBookmark(WIDTH, HEIGHT)

        # search, scroll, then search again
        for i in range(2):
            blue_bookmark = pyautogui.locateCenterOnScreen(BLUE_BOOKMARK_PNG, grayscale=True, confidence=0.6)

            if blue_bookmark:
                buyBookmark(blue_bookmark, WIDTH, HEIGHT)
                print('COVENANT bookmark bought after {} skystones'.format(skystones))
                blue_count += 1
            
            mystic_bookmark = pyautogui.locateCenterOnScreen(MYSTIC_BOOKMARK_PNG, grayscale=True, confidence=0.6)

            if mystic_bookmark:
                buyBookmark(mystic_bookmark, WIDTH, HEIGHT)
                print('MYSTIC bookmark bought after {} skystones'.format(skystones))
                mystic_count += 1
            
            if i == 0: pyautogui.scroll(random.randint(-100, -10))
        
    
    print('''
##################################################################
# 
#            ESSB HAS COMPLETED AND HAS PURCHASED 
#            {} COVENANT AND {} MYSTIC BOOKMARKS
#                       WITH {} SKYSTONES!
#
##################################################################
'''.format(blue_count, mystic_count, skystones)) 

    choice = input('Press enter to exit the program or type "R" to restart the program . . .')
    if (choice.lower() == 'r'):
        repeat = True
    else:
        repeat = False
        sys.exit()
            

if __name__ == '__main__':
    while repeat:
        main()
