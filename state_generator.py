import chess
import chess.pgn
import sys

'''
helper classes:
- Parsing PGN files and storing state information
- Thresholding states by frequency of visit
- reading and writing states/values as text files to skip re-parsing
'''
def generate_nodes(PGN):
    '''
    return dict of all state/value pairs given PGN formatted file names ([str,str,..])
    '''
    all_states = {}
    print('commencing pretraining')
    i = 0
    for f in PGN:
        i+=1
        print('parsing file: ', i,'/',len(PGN))
        with open(f) as pgn:
            Complete = False
            while not Complete:
                try:
                    game = chess.pgn.read_game(pgn)
                    board = game.board()
                    Result = int(game.headers['Result'][0])
                    
                    # black = -1, draw = 0, white = +1
                    if Result == 0:
                        Result = -1
                    elif Result == 0.5:
                        Result = 0

                    for move in game.mainline_moves():
                        try:
                            current = all_states[str(board)] # state seen before
                            all_states[str(board)] = ((current[0]*current[1]+Result)/(current[1]+1),current[1]+1)
                            
                        except KeyError:
                            all_states[str(board)] = (Result, 1)
                        
                        board.push(move)
                        
                except:

                    Complete = True
    
    return all_states

def threshold_nodes(nodes, threshold=100):

    '''
    returns [(state, value, visits)] all nodes {state:(value,visits)} with >= threshold visits
    '''
    states = []
    values = []
    for k in nodes.keys():
        if nodes[k][1] >= threshold:
            states.append(k)
            values.append(nodes[k][0])
    return states, values

def write_data(nodes, name):
    f=open(name,'w')
    for ele in nodes:
        f.write(str(ele)+'\n')

    f.close()

def read_data(name, states = True):
    '''
    returns [states or values] from text file of -> write_data(nodes,name)
    '''
    List = []
    current = ''
    i = 0
    if states:
        for line in open(name):
            current+=str(line.rstrip('\n'))
            i+=1 
            if i % 8 == 0:
                to_add = ''
                for char in current:
                    if char != ' ':
                        to_add+=char
                List.append(to_add)
                current = ''
                to_add = ''

    else:
        List = [line.rstrip('\n') for line in open(name)]
    return List

    
    
    








































                    # move_count+=1

                    # modifier = total_moves-(total_moves-move_count) # weights later states higher
          # total_moves = len(game.mainline_moves())
                # move_count = 0

    
                #    try:
                #         current = all_states[str(board)] # state seen before
                #         all_states[str(board)] = (((current[0]*current[1])+Result*modifier)/(current[1]+modifier),current[1]+modifier)
                #         if all_states[str(board)][0] > 1 or  all_states[str(board)][0] < -1:
                #             print(all_states[str(board)][0])