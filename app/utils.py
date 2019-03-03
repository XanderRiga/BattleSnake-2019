import copy
import math


def distance_to(a, b):
    """"Distance from point a to b"""
    return math.hypot(abs(a['x'] - b['x']), abs(a['y'] - b['y']))

def getadjpoints(point):
    """returns point objects of all of the adjacent points of a given point"""
    superduperpoint = copy.deepcopy(point)

    left = copy.deepcopy(superduperpoint)
    left['x'] = left['x']-1
    # print('left:')
    # print(left)

    right = copy.deepcopy(superduperpoint)
    right['x'] = right['x']+1
    # print('right:')
    # print(right)

    up = copy.deepcopy(superduperpoint)
    up['y'] = up['y']-1
    # print('up')
    # print(up)

    down = copy.deepcopy(superduperpoint)
    down['y'] = down['y']+1
    # print('down')
    # print(down)

    points = [left, right, up, down]
    # print(points)
    return points


def isdiagonal(a, b):
    ax = a["x"]
    ay = a["y"]
    bx = b["x"]
    by = b["y"]

    if abs(ax - bx) == 1 and abs(ay - by) == 1:
        return True
    else:
        return False


def get_snake_heads(snakes, my_id):
    heads = []
    for snake in snakes:
        if snake['id'] != my_id:
            heads.append(snake['body'][0])

    return heads


def diagonaldanger(me, snakes):
    """returns true if there is a dangerous point diagonal of the point"""
    head = me[0]

    for snake in snakes:
        for bodypart in snake['body']:
            if isdiagonal(head, bodypart):
                # print('There is danger diagonally')
                return True

    for point in me[:-1]:
        if isdiagonal(head, point):
            # print('There is danger diagonally')
            return True

    return False


def dirtouchingsnake(point, me, snakes):
    """checks if the point is touching a snake, not including this snakes head or neck"""
    head = me[0]
    neck = me[1]

    dirs = []

    for snake in snakes:
        for bodypart in snake['body']:
            if bodypart not in me:
                adj = findadjacentdir(point, bodypart)
                if adj:
                    dirs.append(adj)

    return dirs


def istouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    self = me[2:]

    for x in self:
        if isadjacentdiagonal(point, x):
            return x

    return False


def dirtouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    dirs = []

    for x in me:
        dir = findadjacentdir(point, x)
        if dir:
            dirs.append(dir)

    return dirs


def dirtouchingwall(point, width, height):
    """returns direction of wall if any"""
    walls = []
    if point['x'] == 0:
        walls.append('left')
    if point['x'] == width - 1:
        walls.append('right')
    if point['y'] == 0:
        walls.append('up')
    if point['y'] == height - 1:
        walls.append('down')

    return walls


def findadjacentdir(a, b):
    """Gives direction from a to b if they are adjacent(not diagonal), if they are not adjacent returns false"""
    ax = a['x']
    ay = a['y']
    bx = b['x']
    by = b['y']
    xdiff = ax - bx
    ydiff = ay - by

    if (xdiff in range(-1, 2) and ydiff == 0) or (ydiff in range(-1, 2) and xdiff == 0):
        if xdiff != 0:
            if xdiff > 0:
                return 'left'
            else:
                return 'right'
        if ydiff != 0:
            if ydiff > 0:
                return 'up'
            else:
                return 'down'
    else:
        return False


def isadjacentdiagonal(a, b):
    """Returns true if a is adjacent to be(with diagonal), if they are not adjacent returns false"""
    ax = a['x']
    ay = a['y']
    bx = b['x']
    by = b['y']
    xdiff = ax - bx
    ydiff = ay - by

    if xdiff in range(-1, 2) and ydiff in range(-1, 2):
        return True
    else:
        return False


def getleft(point):
    newpoint = point
    newpoint['x'] = point['x']-1
    return newpoint


def getright(point):
    newpoint = point
    newpoint['x'] = point['x']+1
    return newpoint


def getup(point):
    newpoint = point
    newpoint['y'] = point['y']-1
    return newpoint


def getdown(point):
    newpoint = point
    newpoint['y'] = point['y']+1
    return newpoint
