import json
import os
import random
import bottle
import copy
import math
import utils

from api import ping_response, start_response, move_response, end_response

directions = ['up', 'down', 'left', 'right']
instadeath = []
danger = {}

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():

    start = {
        'color': '#ffcc00',
        'headType': 'safe',
        'tailType': 'round-bum',
    }

    return start_response(start)


@bottle.post('/move')
def move():
    data = bottle.request.json

    global directions
    global danger
    global instadeath

    directions = ['up', 'down', 'left', 'right']
    danger = {}
    instadeath = []

    data = bottle.request.json

    snakes = data['board']['snakes']
    height = data['board']['height']
    width = data['board']['width']
    food = data['board']['food']

    me = data['you']['body']
    mylength = len(data['you']['body'])
    myhealth = data['you']['health']

    donthitsnakes(me[0], snakes)
    donthitwalls(me, width, height)
    donthittail(me)
    avoidheadtohead(me[0], mylength, snakes)

    if len(directions) == 2 or utils.diagonaldanger(me, snakes):
        # print('doing flood fill checks')
        board = buildboard(me, snakes, width, height)
        zeros = countmatrix0(board)
        # print('zeros: ' + str(zeros))

        headx = me[0]["x"]
        heady = me[0]["y"]

        leftlist = []
        rightlist = []
        uplist = []
        downlist = []
        leftsize = rightsize = upsize = downsize = 0
        # print('directions')
        # print(directions)
        for dir in directions:
            # print('headx: ' + str(headx) + ' heady: ' + str(heady))
            if dir == 'left':
                # print('flood fill on left, x ' + str(headx-1) + ' y: ' + str(heady))
                floodfill(board, headx-1, heady, width, height, leftlist)
                leftsize = len(leftlist)
            if dir == 'right':
                # print('flood fill on right, x ' + str(headx+1) + ' y: ' + str(heady))
                floodfill(board, headx+1, heady, width, height, rightlist)
                rightsize = len(rightlist)
            if dir == 'up':
                # print('flood fill on up, x ' + str(headx) + ' y: ' + str(heady-1))
                floodfill(board, headx, heady-1, width, height, uplist)
                upsize = len(uplist)
            if dir == 'down':
                # print('flood fill on down, x ' + str(headx) + ' y: ' + str(heady+1))
                floodfill(board, headx, heady+1, width, height, downlist)
                downsize = len(downlist)

        # print(leftsize)
        # print(rightsize)
        # print(upsize)
        # print(downsize)
        if leftlist and leftsize < len(me) + 2 and 'left' in directions:
            if 'left' not in danger.keys() or ('left' in danger.keys() and danger['left'] < leftsize):
                danger['left'] = leftsize
            directions.remove('left')
            # print('removing left, size: ' + str(leftsize))
        if leftlist:
            if 'left' not in danger.keys() or ('left' in danger.keys() and danger['left'] < leftsize):
                danger['left'] = leftsize

        if rightlist and rightsize < len(me) + 2 and 'right' in directions:
            if 'right' not in danger.keys() or ('right' in danger.keys() and danger['right'] < rightsize):
                danger['right'] = rightsize
            directions.remove('right')
            # print('removing right, size: ' + str(rightsize))
        if rightlist:
            if 'right' not in danger.keys() or ('right' in danger.keys() and danger['right'] < rightsize):
                danger['right'] = rightsize

        if uplist and upsize < len(me) + 2 and 'up' in directions:
            if 'up' not in danger.keys() or ('up' in danger.keys() and danger['up'] < upsize):
                danger['up'] = upsize
            directions.remove('up')
            # print('removing up, size: ' + str(upsize))
        if uplist:
            if 'up' not in danger.keys() or ('up' in danger.keys() and danger['up'] < upsize):
                danger['up'] = upsize

        if downlist and downsize < len(me) + 2 and 'down' in directions:
            if 'down' not in danger.keys() or ('down' in danger.keys() and danger['down'] < downsize):
                danger['down'] = downsize
            directions.remove('down')
            # print('removing down, size: ' + str(downsize))
        if downlist:
            if 'down' not in danger.keys() or ('down' in danger.keys() and danger['down'] < downsize):
                danger['down'] = downsize


    # print(danger)
    # print(instadeath)
    fooddir = []
    if myhealth < 80:
        closestfood = findclosestfood(me, food)
        if closestfood:
            fooddir = dirtopoint(me, closestfood)

    taunt = 'D.W.I.G.H.T - Determined, Worker, Intense, Good worker, Hard worker, Terrific'
    if directions and len(danger) == 2:
        currsafest = 0
        currdirection = None
        for key, value in danger.items():
            if value > currsafest and key not in instadeath:
                currsafest = value
                currdirection = key

        if currdirection:
            direction = currdirection
    elif directions:
        direction = random.choice(directions)
        if fooddir:
            for x in fooddir:
                if x in directions:
                    direction = x
                    break
    else:
        taunt = 'MICHAEL!!!!!!'
        direction = 'up'
        safest = 0
        # print('We are in danger, here is the direction dict:')
        # print(directions)
        # print('We are in danger, here is the danger dict:')
        # print(danger)
        for key, value in danger.items():
            if value > safest and key not in instadeath:
                safest = value
                direction = key

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    # print(json.dumps(data))

    return end_response()


#
# KENDRAS CODE

def dirtopoint(me, foodpoint):
    """Returns array of directions to foodpoint"""
    global directions
    head = me[0]
    xdiff = abs(head['x'] - foodpoint['x'])
    ydiff = abs(head['y'] - foodpoint['y'])

    newlist = []
    if xdiff >= ydiff and head['x'] - foodpoint['x'] >= 0:
        newlist.append('left')

    if xdiff >= ydiff and head['x'] - foodpoint['x'] < 0:
        newlist.append('right')

    if xdiff < ydiff and head['y'] - foodpoint['y'] >= 0:
        newlist.append('up')

    if xdiff < ydiff and head['y'] - foodpoint['y'] < 0:
        newlist.append('down')

    return newlist


def findclosestfood(me, food):
    """Returns point of food piece that is closest to snake"""
    if (len(food) == 0):
        return False

    head = me[0]
    distance = findpointdistance(head, food[0])
    closestfood = food[0]

    for pieceoffood in food:
        if findpointdistance(head, pieceoffood) < distance:
            closestfood = pieceoffood
            distance = findpointdistance(head, pieceoffood)

    return closestfood


def findpointdistance(a, b):
    """Used to find the closest food"""

    xdiff = a['x'] - b['x']
    ydiff = a['y'] - b['y']

    distance = math.sqrt(xdiff**2 + ydiff**2)

    return distance


def closestsnaketofood(me, snakes, food):
    head = me[0]
    for pieceoffood in food:
        for snake in snakes:
            if findpointdistance(head, pieceoffood) >= findpointdistance(snake['body']['0'], pieceoffood):
                return False
    return True

# END KENDRAS CODE


def printmatrix(matrix):
    for x in range(len(matrix)):
        print(matrix[x])


def floodfill(matrix, x, y, width, height, list):
    """returns a flood filled board from a given point. ALL X AND Y ARE IN REFERENCE TO BOARD COORDS"""
    if matrix[x][y] == 0:
        matrix[x][y] = 1
        list.append(1)

        if x > 0:
            floodfill(matrix, x-1, y, width, height, list)
        if x < width-1:
            floodfill(matrix, x+1, y, width, height, list)
        if y > 0:
            floodfill(matrix, x, y-1, width, height, list)
        if y < height-1:
            floodfill(matrix, x, y+1, width, height, list)


def countmatrix0(matrix):
    count = 0
    for x in range(len(matrix)):
        for y in range(len(matrix[x])):
            if matrix[x][y] == 0:
                count += 1

    return count


def buildboard(me, snakes, width, height):
    matrix = [[0] * height for _ in range(width)]

    for point in me[:-1]:  # cut off last tile of tail since it will be moved for next turn
        x = point['x']
        y = point['y']
        matrix[x][y] = 1

    for snake in snakes:
        for bodypart in snake['body']:
            x = bodypart['x']
            y = bodypart['y']
            matrix[x][y] = 1

    return matrix


# # TODO This is still picking up non dangerous things as danger, and the diagonal stuff isn't working
# def adjacenttodanger(point, me, snakes, width, height):
#     """Checks if point is adjacent to snakes, edge of board, or itself(not neck/head) including diagonally"""
#     if istouchingwall(point, width, height):
#         print('touching wall')
#         return True
#     if istouchingsnake(point, me, snakes):
#         print('touching snake')
#         return True
#     if utils.istouchingself(point, me):
#         print('touching self')
#         return True

def donthitsnakes(head, snakes):
    """goes through entire snake array and stops it from directly hitting any snakes"""
    global directions
    global instadeath

    for snake in snakes:
        for bodypart in snake['body']:
            adj = utils.findadjacentdir(head, bodypart)
            if adj and adj in directions:
                directions.remove(adj)
            if adj and adj not in instadeath:
                instadeath.append(adj)


def donthittail(me):
    """Stops the snake from hitting it's own tail(anything past its head and neck)"""
    global directions
    global instadeath

    head = me[0]

    for x in me[:-1]:  # it is ok to move where the last point in our tail is
        adj = utils.findadjacentdir(head, x)
        if adj and adj in directions:
            directions.remove(adj)
        if adj and adj not in instadeath:
            instadeath.append(adj)


def donthitwalls(me, width, height):
    """Stops the snake from hitting any walls"""
    global directions
    global instadeath

    head = me[0]

    if head['x'] == 0:
        if 'left' in directions:
            directions.remove('left')
        if 'left' not in instadeath:
            instadeath.append('left')
    if head['x'] == width-1:
        if 'right' in directions:
            directions.remove('right')
        if 'right' not in instadeath:
            instadeath.append('right')
    if head['y'] == 0:
        if 'up' in directions:
            directions.remove('up')
        if 'up' not in instadeath:
            instadeath.append('up')
    if head['y'] == height-1:
        if 'down' in directions:
            directions.remove('down')
        if 'down' not in instadeath:
            instadeath.append('down')


def avoidheadtohead(head, mylength, snakes):
    global directions
    global danger
    myadj = utils.getadjpoints(head)

    othersnakeadj = []
    for snake in snakes:
        if snake['body'][0] != head and len(snake['body']) >= mylength:
            snakeadjpts = utils.getadjpoints(snake['body'][0])
            for z in snakeadjpts:
                othersnakeadj.append(z)

    for x in myadj:
        for y in othersnakeadj:
            if x == y:
                dir = utils.findadjacentdir(head, x)
                if dir not in danger:
                    # print('adding ' + str(dir) + 'to danger array with value ' + str(mylength+1))
                    danger[dir] = mylength+1
                if dir and dir in directions:
                    # print('head to head, removing ' + dir)
                    directions.remove(dir)


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
