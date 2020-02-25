import state_generator as sg
from sklearn.neural_network import MLPRegressor
import time
import numpy as np

'''
Simple MLP approach to learn chess state values
- (c) Richard Pienaar 2020
'''

def pretraining(training_files, training=True):
    '''
    evaluates and writes (states.txt, values.txt) thresholded training data [] to working directory
    '''
    
    training_data = sg.generate_nodes(training_files)
    
    if training:
        states, values = sg.threshold_nodes(training_data)
        
        sg.write_data(states, 'statesTraining.txt')
        sg.write_data(values, 'valuesTraining.txt')
    else:
        states, values = sg.threshold_nodes(training_data, threshold=50)

        sg.write_data(states, 'statesTest.txt')
        sg.write_data(values, 'valuesTest.txt')        
    return states, values

def train(states, values):
    '''
    train multilayer perceptron for evaluation of a state based on known state/value pairs 
    - states = [str,str,xx]
    - values = [float,float,xx]
    - return MLPRegressor
    '''
    print('training')
    states_formatted = make_computer_readable(states)
    state_matrix = np.asarray(states_formatted).astype(np.float64)
    value_matrix = np.asarray(values).astype(np.float64)
    model = MLPRegressor(hidden_layer_sizes=(1064,500,50), verbose=True,)
    model.fit(state_matrix, value_matrix)
    return model

def test(model, test_states):
    '''
    model (MLPRegressor), test_states - [str,str,xx]
    '''
    print('testing')
    states_formatted = make_computer_readable(test_states) 
    state_matrix = np.asarray(states_formatted).astype(np.float64)  
    return model.predict(state_matrix)

def workflow(trainingfiles, testingfiles, preTraining=False):
    '''
    all pipelines steps run sequentially
    '''
    start_time = time.time()
    if preTraining:
        pretraining(trainingfiles)
        pretraining(testingfiles, training=False)
    else:
        print('skipping pretraining')
    states = sg.read_data('statesTraining.txt')
    values = sg.read_data('valuesTraining.txt', states=False)
    testing_states = sg.read_data('statesTest.txt')
    testing_values = sg.read_data('valuesTest.txt', states=False)
    # ensure no overlap between testing and training data
    for count, state in enumerate(testing_states):
        if state in states:
            testing_states.remove(state)
            del(testing_values[count])

    value_matrix = np.asarray(testing_values).astype(np.float64)
    model = train(states,values)
    test_output = test(model, testing_states)
    dist = 0
    for i in range(0,len(test_output)):
        dist += abs(test_output[i]-value_matrix[i])
        if abs(test_output[i]-value_matrix[i]) > 0.5:
            print('predicted: ', test_output[i], 'actual: ', value_matrix[i], abs(test_output[i]-value_matrix[i]))
            row = ''
            for count, square in enumerate(testing_states[i]):
               row+=square+' '
               if (count+1)%8 == 0:
                    print(row)
                    row = ''
            print('------------------------')
    
    print('average dist: ', dist / len(test_output), len(test_output))

    print("--- %s seconds ---" % (time.time() - start_time))
    return model

def make_computer_readable(board):
    '''
    str to int representation of pieces in a state
    blank = 0
    pawn = 1
    knight = 2
    bishop = 3
    rook = 5
    queen = 9
    king = 10
    '''
    list_formatted = []
    for state in board:
        IB_list = []
        for element in state:
            if element == ".":
                to_add = 0
            elif element.lower() == "p":
                to_add = 1
            elif element.lower() == 'n':
                to_add = 2
            elif element.lower() == 'b':
                to_add = 3
            elif element.lower() == 'r':
                to_add = 5
            elif element.lower() == 'q':
                to_add = 9
            elif element.lower() == 'k':
                to_add = 10
            if element.islower():
                to_add*= -1
            
            IB_list.append(to_add)
            
        list_formatted.append(IB_list)
    
    return list_formatted
                
def main():
    training_files = ['Alekhine.PGN','twic1318.PGN', 'Aronian.PGN', 'Byrne.PGN', 'Shabalov.PGN', 'Ashley.PGN', 'Andreikin.PGN', 'lichess_db_standard_rated_2013-01.PGN' ]
    testing_files = ['lichess_db_standard_rated_2013-02.PGN']
    workflow(training_files,testing_files, preTraining=False)

if __name__ == "__main__":
    main()