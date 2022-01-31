from collections import namedtuple
import numpy
import random
import os
import sys
import pyautogui
import PIL
import keyboard
import time
import win32gui, win32con


# TODO: catch None pointers whenver script fails (eg. discord notif banner blocks the buy click)
# TODO: gold constraints?
# TODO: alternative stop condition on bookmarks purchased?


######################################################
# 
#               C O N S T A N T S
#
######################################################
SSHOP_SKYSTONE_COST = 3
DELAY_LOWER_BOUND = 0.05
DELAY_UPPER_BOUND = 0.3
CLICK_COUNTS = [i for i in range(2, 4)]

REFRESH_PNG = 'assets/refresh.png'
CONFIRM_PNG = 'assets/confirm.png'
BLUE_BOOKMARK_PNG = 'assets/covenant_bookmark.png'
MYSTIC_BOOKMARK_PNG = 'assets/mystic_bookmark.png'
BUY_PNG = 'assets/buy.png'

STATS = {}
STATS['COVENANTS'] = 0
STATS['MYSTICS'] = 0
STATS['SKYSTONES'] = 0


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
    x = random.gauss((2 * button.left + button.width) / 2, button.width / 7)
    y = random.gauss((2 * button.top + button.height) / 2, button.height / 7)

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
    refreshButton = pyautogui.locateOnScreen(REFRESH_PNG, grayscale=True, confidence=0.6)
    x, y = getGaussianXY(refreshButton)
    delay()

    pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(DELAY_LOWER_BOUND, DELAY_UPPER_BOUND))
    delay()

    confirmButton = pyautogui.locateOnScreen(CONFIRM_PNG, grayscale=True, confidence=0.6)
    x, y = getGaussianXY(confirmButton)

    pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(DELAY_LOWER_BOUND, DELAY_UPPER_BOUND))
    delay()



def buyBookmark(bookmark, win_width, win_height):
    '''
    @param  bookmark
            A tuple of the bookmark icon XY coordinates
    '''
    if bookmark:
        left = bookmark.x + win_width * 0.345 
        width = win_width * 0.110
        top = bookmark.y + win_height * 0.0166
        height = win_height * 0.040

        bookmark_button = Button(left, top, width, height)
        x, y = getGaussianXY(bookmark_button)

        pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(DELAY_LOWER_BOUND, DELAY_UPPER_BOUND))
        delay()

        buy_button = pyautogui.locateOnScreen(BUY_PNG, grayscale=True, confidence=0.6)
        x, y = getGaussianXY(buy_button)

        pyautogui.click(x, y, clicks=random.choice(CLICK_COUNTS), interval=random.uniform(DELAY_LOWER_BOUND, DELAY_UPPER_BOUND))
        delay()


def recordStats(stats):
    # TODO: more stats
    try:
        with open('stats.txt', 'r') as fp:
            for stat in stats:
                line = fp.readline()
                if (line != ''):
                    stats[stat] += int(''.join(filter(str.isdigit, line)))
    except IOError:
        print('stats.txt does not exist, creating now . . .')
    
    with open('stats.txt', 'w') as fp:
        for stat in stats:
            fp.write('{}: {}\n'.format(stat, stats[stat]))


def forceExit():
    recordStats(STATS)
    os._exit(os.X_OK)


######################################################
# 
#                     M A I N
#
######################################################


def main():

    keyboard.add_hotkey('f3', forceExit)

    print(''' 
##################################################################
# 
#   Welcome to the Epic Seven Secret Shop Bookmark Buyer (ESSB)!
#
##################################################################

Ensure that you are in the Secret Shop interface of the game.

The stats.txt file contains a persistent cumulative record of skystones spent vs. bookmarks purchased 
over the course of every time this tool is run.

If the tool fails to work, try:
- Manually taking screenshots of the shop bookmarks similar to the existing ones in /assets
- Editing the global constants in buyer.py.

Once the tool starts, you may press F3 to force abort (do not rely on this).
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

    window_rect = win32gui.GetWindowRect(window)
    WIDTH = window_rect[2] - window_rect[0] 
    HEIGHT = window_rect[3] - window_rect[1]

    time.sleep(0.1)

    for skystones in range(0, skystones_to_spend, SSHOP_SKYSTONE_COST):
        findBookmark(WIDTH, HEIGHT)
        time.sleep(random.uniform(0.2, 0.3))

        STATS['SKYSTONES'] += SSHOP_SKYSTONE_COST

        blue_found, mystic_found = False, False

        # search, scroll, then search again; avoid double counting
        for i in range(2):

            if not blue_found:
                blue_bookmark = pyautogui.locateCenterOnScreen(BLUE_BOOKMARK_PNG, grayscale=True, confidence=0.6)
                if blue_bookmark:
                    buyBookmark(blue_bookmark, WIDTH, HEIGHT) 
                    print('COVENANT bookmark bought after {} skystones'.format(skystones))
                    STATS['COVENANTS'] += 5
                    blue_found = True
            
           
            if not mystic_found: 
                mystic_bookmark = pyautogui.locateCenterOnScreen(MYSTIC_BOOKMARK_PNG, grayscale=True, confidence=0.6)
                if mystic_bookmark:
                    buyBookmark(mystic_bookmark, WIDTH, HEIGHT)
                    print('MYSTIC bookmark bought after {} skystones'.format(skystones))
                    STATS['MYSTICS'] += 50
                    mystic_found = True
            
            if i == 0: 
                pyautogui.moveTo(x=random.uniform(WIDTH * 0.52, WIDTH * 0.75), y=random.uniform(HEIGHT * 0.4, HEIGHT * 0.6))
                pyautogui.scroll(random.randint(-100, -10))
                time.sleep(random.uniform(0.5, 0.8))

    print('''
##################################################################
# 
#                ESSB HAS COMPLETED!
#                {} COVENANT BOOKMARKS ({} Covenant summons)
#                {} MYSTIC BOOKMARKS ({} Mystic summons)
#                {} SKYSTONES USED!
#
##################################################################
'''.format(STATS['COVENANTS'], int(STATS['COVENANTS'] / 5), 
           STATS['MYSTICS'],   int(STATS['MYSTICS'] / 50), 
           STATS['SKYSTONES']))

    recordStats(STATS)

    choice = input('Press enter to exit the program or type "R" to restart the program . . .')
    if (choice.lower() == 'r'):
        repeat = True
    else:
        repeat = False
        sys.exit()
            

if __name__ == '__main__':
    while repeat:
        main()
